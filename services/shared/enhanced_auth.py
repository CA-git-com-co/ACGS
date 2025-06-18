"""
Enhanced ACGS Authentication Service
High-performance authentication with Redis caching, connection pooling, and advanced security
"""

import json
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import aioredis
import jwt
from jwt import InvalidTokenError as JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Production-grade Configuration
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "acgs-production-secret-key-2024-constitutional-governance-jwt-signing-v2",
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)  # Reduced for security
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Service-to-service authentication
SERVICE_SECRET_KEY = os.environ.get(
    "SERVICE_SECRET_KEY",
    "acgs-service-to-service-secret-key-2024-constitutional-governance-internal-auth",
)
SERVICE_TOKEN_EXPIRE_MINUTES = int(os.environ.get("SERVICE_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing with enhanced security rounds
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=15,  # SECURITY: Increased from 12 to 15 for enhanced security
)

# Security scheme
security = HTTPBearer()


class UserRole(Enum):
    """Enhanced user roles in the ACGS constitutional governance system."""

    # Administrative roles
    SYSTEM_ADMIN = "system_admin"
    CONSTITUTIONAL_ADMIN = "constitutional_admin"

    # Governance roles
    CONSTITUTIONAL_COUNCIL = "constitutional_council"
    POLICY_ANALYST = "policy_analyst"
    GOVERNANCE_REVIEWER = "governance_reviewer"

    # Service roles
    SERVICE_ACCOUNT = "service_account"
    INTERNAL_SERVICE = "internal_service"

    # Public access
    PUBLIC_GUEST = "public_guest"
    AUTHENTICATED_USER = "authenticated_user"


class ConstitutionalPermission(Enum):
    """Constitutional governance permissions."""

    # Constitutional management
    CONSTITUTIONAL_READ = "constitutional:read"
    CONSTITUTIONAL_WRITE = "constitutional:write"
    CONSTITUTIONAL_ADMIN = "constitutional:admin"

    # Policy management
    POLICY_CREATE = "policy:create"
    POLICY_REVIEW = "policy:review"
    POLICY_APPROVE = "policy:approve"
    POLICY_ENFORCE = "policy:enforce"

    # Governance workflows
    GOVERNANCE_INITIATE = "governance:initiate"
    GOVERNANCE_PARTICIPATE = "governance:participate"
    GOVERNANCE_OVERSEE = "governance:oversee"

    # System administration
    SYSTEM_ADMIN = "system:admin"
    SERVICE_MANAGE = "service:manage"
    AUDIT_ACCESS = "audit:access"

    # WINA oversight
    WINA_OVERSIGHT = "wina:oversight"
    WINA_INTERVENTION = "wina:intervention"


class ServicePermission(Enum):
    """Service-specific permissions."""

    # Authentication service
    AUTH_MANAGE_USERS = "auth:manage_users"
    AUTH_MANAGE_ROLES = "auth:manage_roles"

    # Constitutional AI service
    AC_VALIDATE_PRINCIPLES = "ac:validate_principles"
    AC_MANAGE_CONSTITUTION = "ac:manage_constitution"

    # Policy Governance service
    PGC_ENFORCE_POLICIES = "pgc:enforce_policies"
    PGC_VALIDATE_COMPLIANCE = "pgc:validate_compliance"

    # Governance Synthesis service
    GS_SYNTHESIZE_POLICIES = "gs:synthesize_policies"
    GS_MANAGE_WORKFLOWS = "gs:manage_workflows"

    # Formal Verification service
    FV_VERIFY_POLICIES = "fv:verify_policies"
    FV_MATHEMATICAL_PROOF = "fv:mathematical_proof"

    # Integrity service
    INTEGRITY_CRYPTOGRAPHIC = "integrity:cryptographic"
    INTEGRITY_AUDIT_TRAIL = "integrity:audit_trail"

    # Evolutionary Computation service
    EC_WINA_OVERSIGHT = "ec:wina_oversight"
    EC_SYSTEM_EVOLUTION = "ec:system_evolution"


class SessionStatus(Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class User:
    """Enhanced user model for ACGS authentication."""

    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None = None
    login_attempts: int = 0
    locked_until: datetime | None = None

    # Security features
    mfa_enabled: bool = False
    password_changed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    failed_login_attempts: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert user to dictionary for caching."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "mfa_enabled": self.mfa_enabled,
            "password_changed_at": self.password_changed_at.isoformat(),
            "failed_login_attempts": self.failed_login_attempts,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        """Create user from dictionary."""
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            role=UserRole(data["role"]),
            is_active=data["is_active"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_login=(
                datetime.fromisoformat(data["last_login"])
                if data["last_login"]
                else None
            ),
            mfa_enabled=data.get("mfa_enabled", False),
            password_changed_at=datetime.fromisoformat(data["password_changed_at"]),
            failed_login_attempts=data.get("failed_login_attempts", 0),
        )


@dataclass
class TokenData:
    """Enhanced token payload data."""

    user_id: str
    username: str
    role: str
    exp: int
    iat: int
    jti: str  # JWT ID for token tracking
    service: str | None = None
    session_id: str | None = None


@dataclass
class UserSession:
    """User session tracking."""

    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    status: SessionStatus = SessionStatus.ACTIVE

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary for caching."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "status": self.status.value,
        }


class AuthenticationError(Exception):
    """Authentication related errors."""

    pass


class AuthorizationError(Exception):
    """Authorization related errors."""

    pass


class EnhancedAuthService:
    """High-performance authentication service with Redis caching."""

    def __init__(self, redis_url: str | None = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.redis_url = redis_url or "redis://localhost:6379"
        self.redis_client: aioredis.Redis | None = None

        # In-memory fallback storage
        self.users_db: dict[str, dict[str, Any]] = {}
        self.active_tokens: set[str] = set()
        self.active_sessions: dict[str, UserSession] = {}

        # Performance metrics
        self.auth_metrics = {
            "total_authentications": 0,
            "successful_authentications": 0,
            "failed_authentications": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_auth_time": 0.0,
        }

        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.session_timeout = timedelta(hours=8)

        # Create default users
        self._create_default_users()

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize Redis connection and load users."""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
            logger.info("Redis connection established for auth service")

            # Load users from cache
            await self._load_users_from_cache()

        except Exception as e:
            logger.warning(f"Failed to initialize Redis for auth service: {e}")
            logger.info("Falling back to in-memory storage")

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    def _create_default_users(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Create default users for testing."""
        default_users = [
            {
                "id": "admin_001",
                "username": "admin",
                "email": "admin@acgs.local",
                "role": UserRole.SYSTEM_ADMIN,
                "password": "admin_password",
            },
            {
                "id": "council_001",
                "username": "council_member",
                "email": "council@acgs.local",
                "role": UserRole.CONSTITUTIONAL_COUNCIL,
                "password": "council_password",
            },
            {
                "id": "analyst_001",
                "username": "policy_analyst",
                "email": "analyst@acgs.local",
                "role": UserRole.POLICY_ANALYST,
                "password": "analyst_password",
            },
        ]

        for user_data in default_users:
            password = user_data.pop("password")
            user = User(**user_data)

            self.users_db[user.username] = {
                "user": user,
                "password_hash": self.hash_password(password),
            }

    async def _load_users_from_cache(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Load users from Redis cache."""
        if not self.redis_client:
            return

        try:
            # Load all user keys
            user_keys = await self.redis_client.keys("user:*")

            for key in user_keys:
                user_data = await self.redis_client.hgetall(key)
                if user_data:
                    username = key.split(":")[-1]
                    user = User.from_dict(user_data["user_info"])
                    password_hash = user_data["password_hash"]

                    self.users_db[username] = {
                        "user": user,
                        "password_hash": password_hash,
                    }

            logger.info(f"Loaded {len(user_keys)} users from cache")

        except Exception as e:
            logger.error(f"Failed to load users from cache: {e}")

    async def _cache_user(self, username: str, user: User, password_hash: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cache user data in Redis."""
        if not self.redis_client:
            return

        try:
            user_key = f"user:{username}"
            await self.redis_client.hset(
                user_key,
                mapping={
                    "user_info": json.dumps(user.to_dict()),
                    "password_hash": password_hash,
                },
            )
            await self.redis_client.expire(user_key, 3600)  # 1 hour TTL

        except Exception as e:
            logger.error(f"Failed to cache user {username}: {e}")

    def hash_password(self, password: str) -> str:
        """Hash a password with optimized settings."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
    ) -> User | None:
        """Enhanced user authentication with caching and security features."""
        start_time = time.time()

        try:
            # Check cache first
            cached_user = await self._get_cached_user(username)
            if cached_user:
                self.auth_metrics["cache_hits"] += 1
                user_data = cached_user
            else:
                self.auth_metrics["cache_misses"] += 1
                user_data = self.users_db.get(username)

                if user_data:
                    # Cache for future use
                    await self._cache_user(
                        username, user_data["user"], user_data["password_hash"]
                    )

            if not user_data:
                self._update_auth_metrics(time.time() - start_time, False)
                return None

            user = user_data["user"]

            # Check if user is locked
            if user.locked_until and user.locked_until > datetime.now(UTC):
                raise AuthenticationError(f"Account locked until {user.locked_until}")

            # Verify password
            if not self.verify_password(password, user_data["password_hash"]):
                # Increment failed attempts
                user.failed_login_attempts += 1

                # Lock account if too many failures
                if user.failed_login_attempts >= self.max_login_attempts:
                    user.locked_until = (
                        datetime.now(UTC) + self.lockout_duration
                    )
                    logger.warning(
                        f"Account {username} locked due to too many failed attempts"
                    )

                await self._cache_user(username, user, user_data["password_hash"])
                self._update_auth_metrics(time.time() - start_time, False)
                return None

            # Check if user is active
            if not user.is_active:
                self._update_auth_metrics(time.time() - start_time, False)
                return None

            # Successful authentication
            user.last_login = datetime.now(UTC)
            user.failed_login_attempts = 0
            user.locked_until = None

            # Create session
            await self._create_session(user, ip_address, user_agent)

            # Update cache
            await self._cache_user(username, user, user_data["password_hash"])

            self._update_auth_metrics(time.time() - start_time, True)
            return user

        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            self._update_auth_metrics(time.time() - start_time, False)
            raise AuthenticationError(str(e))

    async def _get_cached_user(self, username: str) -> dict[str, Any] | None:
        """Get user from cache."""
        if not self.redis_client:
            return None

        try:
            user_key = f"user:{username}"
            user_data = await self.redis_client.hgetall(user_key)

            if user_data and "user_info" in user_data:
                user_info = json.loads(user_data["user_info"])
                user = User.from_dict(user_info)

                return {"user": user, "password_hash": user_data["password_hash"]}

        except Exception as e:
            logger.debug(f"Cache lookup failed for {username}: {e}")

        return None

    async def _create_session(
        self, user: User, ip_address: str, user_agent: str
    ) -> UserSession:
        """Create a new user session."""
        session_id = secrets.token_urlsafe(32)

        session = UserSession(
            session_id=session_id,
            user_id=user.id,
            created_at=datetime.now(UTC),
            last_activity=datetime.now(UTC),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Store session
        self.active_sessions[session_id] = session

        # Cache session in Redis
        if self.redis_client:
            try:
                session_key = f"session:{session_id}"
                await self.redis_client.setex(
                    session_key,
                    int(self.session_timeout.total_seconds()),
                    json.dumps(session.to_dict()),
                )
            except Exception as e:
                logger.error(f"Failed to cache session: {e}")

        return session

    async def create_access_token(
        self,
        user: User,
        session_id: str | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create an access token with enhanced security."""
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )

        # Generate unique JWT ID
        jti = secrets.token_urlsafe(16)

        to_encode = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.now(UTC),
            "jti": jti,
            "service": "acgs",
            "session_id": session_id,
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        # Store token in active set and cache
        self.active_tokens.add(jti)

        if self.redis_client:
            try:
                token_key = f"token:{jti}"
                await self.redis_client.setex(
                    token_key,
                    int((expire - datetime.now(UTC)).total_seconds()),
                    json.dumps(
                        {
                            "user_id": user.id,
                            "username": user.username,
                            "role": user.role.value,
                            "session_id": session_id,
                        }
                    ),
                )
            except Exception as e:
                logger.error(f"Failed to cache token: {e}")

        return encoded_jwt

    async def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token with caching."""
        try:
            # Decode token to get JTI
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False}
            )
            jti = payload.get("jti")

            if not jti:
                raise AuthenticationError("Invalid token format")

            # Check if token is revoked (cache first)
            if self.redis_client:
                try:
                    token_key = f"token:{jti}"
                    cached_token = await self.redis_client.get(token_key)

                    if not cached_token:
                        raise AuthenticationError("Token has been revoked or expired")

                except Exception as e:
                    logger.debug(f"Token cache lookup failed: {e}")
                    # Fall back to in-memory check
                    if jti not in self.active_tokens:
                        raise AuthenticationError("Token has been revoked")
            else:
                if jti not in self.active_tokens:
                    raise AuthenticationError("Token has been revoked")

            # Verify token with expiration
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            token_data = TokenData(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                role=payload.get("role"),
                exp=payload.get("exp"),
                iat=payload.get("iat"),
                jti=jti,
                service=payload.get("service"),
                session_id=payload.get("session_id"),
            )

            return token_data

        except ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    def _update_auth_metrics(self, response_time: float, success: bool):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update authentication metrics."""
        self.auth_metrics["total_authentications"] += 1

        if success:
            self.auth_metrics["successful_authentications"] += 1
        else:
            self.auth_metrics["failed_authentications"] += 1

        # Update average response time
        alpha = 0.1
        self.auth_metrics["avg_auth_time"] = (
            alpha * response_time + (1 - alpha) * self.auth_metrics["avg_auth_time"]
        )

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get authentication performance metrics."""
        total_auths = self.auth_metrics["total_authentications"]
        success_rate = (
            self.auth_metrics["successful_authentications"] / total_auths
            if total_auths > 0
            else 1.0
        )

        cache_total = (
            self.auth_metrics["cache_hits"] + self.auth_metrics["cache_misses"]
        )
        cache_hit_rate = (
            self.auth_metrics["cache_hits"] / cache_total if cache_total > 0 else 0.0
        )

        return {
            "total_authentications": total_auths,
            "success_rate": success_rate,
            "avg_auth_time": self.auth_metrics["avg_auth_time"],
            "cache_hit_rate": cache_hit_rate,
            "active_sessions": len(self.active_sessions),
            "active_tokens": len(self.active_tokens),
        }


# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.SYSTEM_ADMIN: [
        ConstitutionalPermission.CONSTITUTIONAL_ADMIN,
        ConstitutionalPermission.POLICY_APPROVE,
        ConstitutionalPermission.GOVERNANCE_OVERSEE,
        ConstitutionalPermission.SYSTEM_ADMIN,
        ConstitutionalPermission.SERVICE_MANAGE,
        ConstitutionalPermission.AUDIT_ACCESS,
        ConstitutionalPermission.WINA_OVERSIGHT,
        ConstitutionalPermission.WINA_INTERVENTION,
        # All service permissions
        ServicePermission.AUTH_MANAGE_USERS,
        ServicePermission.AUTH_MANAGE_ROLES,
        ServicePermission.AC_MANAGE_CONSTITUTION,
        ServicePermission.PGC_ENFORCE_POLICIES,
        ServicePermission.GS_MANAGE_WORKFLOWS,
        ServicePermission.FV_MATHEMATICAL_PROOF,
        ServicePermission.INTEGRITY_CRYPTOGRAPHIC,
        ServicePermission.EC_SYSTEM_EVOLUTION,
    ],
    UserRole.CONSTITUTIONAL_ADMIN: [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
        ConstitutionalPermission.CONSTITUTIONAL_WRITE,
        ConstitutionalPermission.CONSTITUTIONAL_ADMIN,
        ConstitutionalPermission.POLICY_APPROVE,
        ConstitutionalPermission.GOVERNANCE_OVERSEE,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
        ServicePermission.AC_MANAGE_CONSTITUTION,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
        ServicePermission.INTEGRITY_AUDIT_TRAIL,
    ],
    UserRole.CONSTITUTIONAL_COUNCIL: [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
        ConstitutionalPermission.CONSTITUTIONAL_WRITE,
        ConstitutionalPermission.POLICY_REVIEW,
        ConstitutionalPermission.POLICY_APPROVE,
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
        ServicePermission.GS_SYNTHESIZE_POLICIES,
    ],
    UserRole.POLICY_ANALYST: [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
        ConstitutionalPermission.POLICY_CREATE,
        ConstitutionalPermission.POLICY_REVIEW,
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
        ServicePermission.GS_SYNTHESIZE_POLICIES,
        ServicePermission.FV_VERIFY_POLICIES,
    ],
    UserRole.GOVERNANCE_REVIEWER: [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
        ConstitutionalPermission.POLICY_REVIEW,
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
    ],
    UserRole.SERVICE_ACCOUNT: [
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
        ServicePermission.INTEGRITY_AUDIT_TRAIL,
    ],
    UserRole.INTERNAL_SERVICE: [
        # Internal services have broad access for system operations
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
        ServicePermission.GS_SYNTHESIZE_POLICIES,
        ServicePermission.FV_VERIFY_POLICIES,
        ServicePermission.INTEGRITY_AUDIT_TRAIL,
        ServicePermission.EC_WINA_OVERSIGHT,
    ],
    UserRole.AUTHENTICATED_USER: [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
    ],
    UserRole.PUBLIC_GUEST: [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
    ],
}


class PermissionChecker:
    """Enhanced permission checking for constitutional governance."""

    @staticmethod
    def has_permission(
        user: User, permission: ConstitutionalPermission | ServicePermission
    ) -> bool:
        """Check if user has a specific permission."""
        user_permissions = ROLE_PERMISSIONS.get(user.role, [])
        return permission in user_permissions

    @staticmethod
    def has_any_permission(
        user: User, permissions: list[ConstitutionalPermission | ServicePermission]
    ) -> bool:
        """Check if user has any of the specified permissions."""
        user_permissions = ROLE_PERMISSIONS.get(user.role, [])
        return any(permission in user_permissions for permission in permissions)

    @staticmethod
    def has_all_permissions(
        user: User, permissions: list[ConstitutionalPermission | ServicePermission]
    ) -> bool:
        """Check if user has all of the specified permissions."""
        user_permissions = ROLE_PERMISSIONS.get(user.role, [])
        return all(permission in user_permissions for permission in permissions)

    @staticmethod
    def get_user_permissions(
        user: User,
    ) -> list[ConstitutionalPermission | ServicePermission]:
        """Get all permissions for a user."""
        return ROLE_PERMISSIONS.get(user.role, [])


def require_permission(permission: ConstitutionalPermission | ServicePermission):
    """Decorator to require specific permission for endpoint access."""

    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not PermissionChecker.has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}",
            )
        return current_user

    return permission_checker


def require_any_permission(
    permissions: list[ConstitutionalPermission | ServicePermission],
):
    """Decorator to require any of the specified permissions."""

    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not PermissionChecker.has_any_permission(current_user, permissions):
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required any of: {', '.join(permission_names)}",
            )
        return current_user

    return permission_checker


def require_role(role: UserRole):
    """Decorator to require specific role for endpoint access."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {role.value}, Current: {current_user.role.value}",
            )
        return current_user

    return role_checker


# Service-to-service authentication
class ServiceAuthManager:
    """Manages service-to-service authentication."""

    @staticmethod
    def create_service_token(service_name: str, permissions: list[str] = None) -> str:
        """Create a service-to-service authentication token."""
        if permissions is None:
            permissions = ["internal_service"]

        expire = datetime.now(UTC) + timedelta(
            minutes=SERVICE_TOKEN_EXPIRE_MINUTES
        )
        jti = secrets.token_urlsafe(16)

        payload = {
            "service_name": service_name,
            "permissions": permissions,
            "exp": expire,
            "iat": datetime.now(UTC),
            "jti": jti,
            "type": "service_token",
        }

        return jwt.encode(payload, SERVICE_SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_service_token(token: str) -> dict[str, Any]:
        """Verify a service-to-service token."""
        try:
            payload = jwt.decode(token, SERVICE_SECRET_KEY, algorithms=[ALGORITHM])

            if payload.get("type") != "service_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid service token type",
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Service token has expired",
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid service token"
            )


async def get_service_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Dependency for service-to-service authentication."""
    return ServiceAuthManager.verify_service_token(credentials.credentials)


# Global enhanced auth service instance
enhanced_auth_service = EnhancedAuthService()


# FastAPI dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current authenticated user with enhanced performance."""
    try:
        token = credentials.credentials
        token_data = await enhanced_auth_service.verify_token(token)

        # Get user from cache first
        cached_user = await enhanced_auth_service._get_cached_user(token_data.username)
        if cached_user:
            return cached_user["user"]

        # Fallback to in-memory lookup
        user_data = enhanced_auth_service.users_db.get(token_data.username)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_data["user"]

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# Export main functions and classes
__all__ = [
    "User",
    "UserRole",
    "ConstitutionalPermission",
    "ServicePermission",
    "TokenData",
    "UserSession",
    "EnhancedAuthService",
    "enhanced_auth_service",
    "get_current_user",
    "get_service_auth",
    "PermissionChecker",
    "ServiceAuthManager",
    "require_permission",
    "require_any_permission",
    "require_role",
    "AuthenticationError",
    "AuthorizationError",
    "ROLE_PERMISSIONS",
]
