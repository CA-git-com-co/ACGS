# ACGS/shared/schemas.py
from datetime import datetime
from typing import Any
from uuid import UUID  # For UUID validation if used in models

from pydantic import BaseModel, EmailStr, Field


# Base Pydantic model for common settings
class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}


# Token Schemas (originally from auth_service/app/schemas/token.py)
class Token(BaseSchema):
    access_token: str
    refresh_token: str | None = (
        None  # Refresh token might not always be sent with access token
    )
    token_type: str = "bearer"


class TokenPayload(
    BaseModel
):  # Not inheriting BaseSchema as it's for internal processing
    sub: str | None = None  # Subject (user identifier, e.g., username or user ID)
    user_id: UUID | None = None  # UUID for User.id
    # Add any other claims you expect in the token payload (e.g., roles, permissions)
    # exp: Optional[int] = None # Expiration time (handled by JWT library)


class RefreshTokenCreate(BaseModel):
    user_id: UUID  # UUID for User.id
    jti: str
    token: str  # The actual refresh token string
    expires_at: datetime


class RefreshTokenSchema(RefreshTokenCreate):
    id: int
    created_at: datetime
    is_revoked: bool

    model_config = {"from_attributes": True}


# User Schemas (originally from auth_service/app/schemas/user.py)
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str | None = Field(None, max_length=255)
    role: str = Field("user", max_length=50)  # Default role
    is_active: bool | None = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    password: str | None = Field(None, min_length=8)
    username: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=255)
    role: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class UserSchema(UserBase):  # For reading user data (doesn't include password)
    id: int  # Or UUID
    created_at: datetime
    updated_at: datetime


# Response model for user list, could include pagination later
class UserListResponse(BaseSchema):
    users: list[UserSchema]
    total: int


# Principle Schemas (for ac_service)
class PrincipleBase(BaseSchema):
    name: str = Field(..., max_length=255)
    description: str | None = None
    content: str
    version: int | None = 1
    status: str | None = Field("draft", max_length=50)


class PrincipleCreate(PrincipleBase):
    pass


class PrincipleUpdate(PrincipleBase):
    name: str | None = Field(None, max_length=255)
    content: str | None = None
    version: int | None = None
    status: str | None = Field(None, max_length=50)


class PrincipleSchema(PrincipleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_user_id: int | None = None  # Or UUID


# PolicyRule Schemas (for integrity_service, gs_service, pgc_service)
class PolicyRuleBase(BaseSchema):
    rule_name: str | None = Field(None, max_length=255)
    datalog_content: str
    version: int | None = 1
    policy_id: int | None = None  # Link to parent Policy
    source_principle_ids: list[int] | None = None
    status: str | None = Field("pending_synthesis", max_length=50)
    verification_status: str | None = Field("not_verified", max_length=50)
    verification_feedback: dict[str, Any] | None = None

    # Enhanced fields for audit findings
    framework: str | None = Field(
        "Datalog",
        max_length=50,
        description="Policy framework: Datalog, Rego, JSON, YAML",
    )
    principle_text: str | None = Field(
        None, description="Human-readable principle description"
    )
    pgp_signature: str | None = Field(
        None, description="PGP signature for integrity verification"
    )
    source_file: str | None = Field(
        None, max_length=500, description="Source file path for provenance"
    )
    content_hash: str | None = Field(
        None, max_length=128, description="SHA-256 hash of rule content"
    )
    import_dependencies: list[str] | None = Field(
        None, description="List of external modules/imports required"
    )


class PolicyRuleCreate(PolicyRuleBase):
    datalog_content: str = Field(...)  # Make mandatory for creation


class PolicyRuleUpdate(PolicyRuleBase):
    datalog_content: str | None = None  # Allow partial updates
    # Other fields can be updated as needed


class PolicyRuleSchema(PolicyRuleBase):
    id: int
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    synthesized_by_gs_run_id: str | None = None
    verified_by_fv_run_id: str | None = None


# AuditLog Schemas (for integrity_service)
class AuditLogBase(BaseSchema):
    service_name: str = Field(..., max_length=100)
    event_type: str = Field(..., max_length=100)
    actor_id: int | None = None  # Or UUID
    entity_type: str | None = Field(None, max_length=100)
    entity_id_int: int | None = None
    entity_id_uuid: UUID | None = None
    entity_id_str: str | None = Field(None, max_length=255)
    description: str | None = None
    details: dict[str, Any] | None = None


class AuditLogCreate(AuditLogBase):
    pass  # timestamp is auto-generated


class AuditLogSchema(AuditLogBase):
    id: UUID  # Assuming AuditLog.id is UUID
    timestamp: datetime


# PolicyTemplate Schemas (for gs_service)
class PolicyTemplateBase(BaseSchema):
    name: str = Field(..., max_length=255)
    description: str | None = None
    template_content: str
    parameters_schema: dict[str, Any] | None = None  # JSON Schema for parameters
    version: int | None = 1
    status: str | None = Field("draft", max_length=50)


class PolicyTemplateCreate(PolicyTemplateBase):
    pass


class PolicyTemplateUpdate(PolicyTemplateBase):
    name: str | None = Field(None, max_length=255)
    template_content: str | None = None
    # Allow other fields to be updatable


class PolicyTemplateSchema(PolicyTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_user_id: int | None = None  # Or UUID


# Policy Schemas (for gs_service)
class PolicyBase(BaseSchema):
    name: str = Field(..., max_length=255)
    description: str | None = None
    high_level_content: str | None = None
    version: int | None = 1
    status: str | None = Field("draft", max_length=50)
    template_id: int | None = None
    customization_parameters: dict[str, Any] | None = None
    source_principle_ids: list[int] | None = None


class PolicyCreate(PolicyBase):
    name: str = Field(..., max_length=255)  # Ensure name is provided on create


class PolicyUpdate(PolicyBase):
    name: str | None = Field(None, max_length=255)
    # Allow other fields to be updatable


class PolicySchema(PolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_user_id: int | None = None  # Or UUID
    rules: list[PolicyRuleSchema] | None = []  # Show associated rules


# Generic message schema for responses
class Message(BaseSchema):
    message: str


# Schema for ID response
class IdResponse(BaseSchema):
    id: Any
