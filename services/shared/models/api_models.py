"""
Shared API Models
Constitutional Hash: cdd01ef066bc6cf2

This module provides Pydantic models for structured API payloads to improve
type safety and validation across all ACGS services.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from pydantic.types import NonNegativeInt, PositiveInt

from ..constants import (
    CONSTITUTIONAL_HASH,
    PATTERNS,
    EnvironmentTypes,
    MessagePriorities,
)


class ConstitutionalValidationMixin(BaseModel):
    """Mixin for constitutional validation in all models."""

    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH,
        description="Constitutional compliance hash",
        regex=PATTERNS["CONSTITUTIONAL_HASH"],
    )

    @validator("constitutional_hash")
    def validate_constitutional_hash(cls, v):
        """Validate constitutional hash matches expected value."""
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(
                f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, got {v}"
            )
        return v


class BaseRequest(ConstitutionalValidationMixin):
    """Base request model with common fields."""

    request_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique request identifier"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Request timestamp",
    )
    service_name: str | None = Field(None, description="Name of the requesting service")
    tenant_id: str | None = Field(
        None, description="Tenant identifier for multi-tenant systems"
    )
    user_id: str | None = Field(None, description="User identifier")


class BaseResponse(ConstitutionalValidationMixin):
    """Base response model with common fields."""

    request_id: str = Field(
        ..., description="Request identifier from the original request"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp",
    )
    status: str = Field("success", description="Response status")
    message: str | None = Field(None, description="Response message")


class ErrorResponse(BaseResponse):
    """Standard error response model."""

    status: str = Field("error", description="Error status")
    error_code: str = Field(..., description="Application-specific error code")
    details: dict[str, Any] | None = Field(None, description="Additional error details")

    class Config:
        schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-01-01T00:00:00Z",
                "status": "error",
                "error_code": "AUTH_001",
                "message": "Authentication required",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }
        }


class HealthCheckResponse(BaseResponse):
    """Health check response model."""

    service_name: str = Field(..., description="Name of the service")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    dependencies: dict[str, str] = Field(
        default_factory=dict, description="Dependency health status"
    )

    class Config:
        schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-01-01T00:00:00Z",
                "status": "success",
                "service_name": "constitutional-ai",
                "version": "3.0.0",
                "uptime": 86400.0,
                "dependencies": {"database": "healthy", "redis": "healthy"},
                "constitutional_hash": "cdd01ef066bc6cf2",
            }
        }


class PaginationRequest(BaseModel):
    """Pagination request parameters."""

    page: PositiveInt = Field(1, description="Page number (1-indexed)")
    page_size: PositiveInt = Field(50, le=500, description="Number of items per page")
    sort_by: str | None = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", regex="^(asc|desc)$", description="Sort order")


class PaginationResponse(BaseModel):
    """Pagination response metadata."""

    page: PositiveInt = Field(..., description="Current page number")
    page_size: PositiveInt = Field(..., description="Items per page")
    total_items: NonNegativeInt = Field(..., description="Total number of items")
    total_pages: NonNegativeInt = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseResponse):
    """Paginated response model."""

    data: list[Any] = Field(..., description="List of items")
    pagination: PaginationResponse = Field(..., description="Pagination metadata")


# Authentication and Authorization Models
class LoginRequest(BaseRequest):
    """User login request."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    remember_me: bool = Field(False, description="Whether to remember the session")


class TokenResponse(BaseResponse):
    """Authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: str | None = Field(None, description="Refresh token")


class UserInfo(BaseModel):
    """User information model."""

    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., regex=PATTERNS["EMAIL"], description="User email")
    roles: list[str] = Field(default_factory=list, description="User roles")
    tenant_id: str | None = Field(None, description="Tenant identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: datetime | None = Field(None, description="Last login timestamp")


# Constitutional AI Models
class ConstitutionalPrinciple(BaseModel):
    """Constitutional principle model."""

    principle_id: str = Field(..., description="Unique principle identifier")
    name: str = Field(..., description="Principle name")
    description: str = Field(..., description="Principle description")
    category: str = Field(..., description="Principle category")
    priority: MessagePriorities = Field(..., description="Principle priority")
    active: bool = Field(True, description="Whether the principle is active")


class ConstitutionalValidationRequest(BaseRequest):
    """Request for constitutional validation."""

    content: str = Field(..., description="Content to validate")
    context: dict[str, Any] | None = Field(None, description="Additional context")
    principles: list[str] | None = Field(
        None, description="Specific principles to validate against"
    )
    strict_mode: bool = Field(False, description="Whether to use strict validation")


class ConstitutionalValidationResponse(BaseResponse):
    """Response from constitutional validation."""

    is_compliant: bool = Field(
        ..., description="Whether content is constitutionally compliant"
    )
    compliance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Compliance score (0-1)"
    )
    violations: list[dict[str, Any]] = Field(
        default_factory=list, description="List of violations found"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improvement"
    )


# Policy and Governance Models
class PolicyRule(BaseModel):
    """Policy rule model."""

    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    condition: str = Field(..., description="Rule condition (OPA Rego or similar)")
    action: str = Field(..., description="Action to take when rule matches")
    priority: int = Field(..., ge=1, le=100, description="Rule priority")
    enabled: bool = Field(True, description="Whether the rule is enabled")
    tags: list[str] = Field(default_factory=list, description="Rule tags")


class PolicyEvaluationRequest(BaseRequest):
    """Request for policy evaluation."""

    input_data: dict[str, Any] = Field(
        ..., description="Input data for policy evaluation"
    )
    policy_name: str | None = Field(None, description="Specific policy to evaluate")
    environment: EnvironmentTypes = Field(
        EnvironmentTypes.PRODUCTION, description="Environment context"
    )


class PolicyEvaluationResponse(BaseResponse):
    """Response from policy evaluation."""

    decision: str = Field(..., description="Policy decision (allow/deny/abstain)")
    matched_rules: list[str] = Field(
        default_factory=list, description="Rules that matched"
    )
    execution_time: float = Field(
        ..., description="Policy evaluation time in milliseconds"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Additional evaluation metadata"
    )


# Service Mesh and Communication Models
class ServiceRegistration(BaseModel):
    """Service registration model."""

    service_name: str = Field(..., description="Service name")
    service_id: str = Field(..., description="Unique service instance identifier")
    host: str = Field(..., description="Service host")
    port: int = Field(..., ge=1, le=65535, description="Service port")
    health_check_endpoint: str = Field("/health", description="Health check endpoint")
    tags: list[str] = Field(default_factory=list, description="Service tags")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Service metadata"
    )


class ServiceDiscoveryRequest(BaseRequest):
    """Service discovery request."""

    service_name: str = Field(..., description="Name of service to discover")
    tags: list[str] | None = Field(None, description="Required tags")
    healthy_only: bool = Field(True, description="Return only healthy instances")


class ServiceDiscoveryResponse(BaseResponse):
    """Service discovery response."""

    services: list[ServiceRegistration] = Field(
        ..., description="List of discovered services"
    )


# Monitoring and Metrics Models
class MetricPoint(BaseModel):
    """Individual metric point."""

    timestamp: datetime = Field(..., description="Metric timestamp")
    value: float = Field(..., description="Metric value")
    labels: dict[str, str] = Field(default_factory=dict, description="Metric labels")


class MetricSeries(BaseModel):
    """Time series metric data."""

    metric_name: str = Field(..., description="Metric name")
    points: list[MetricPoint] = Field(..., description="Metric data points")


class PerformanceMetrics(BaseModel):
    """Performance metrics model."""

    request_count: int = Field(..., description="Total request count")
    avg_response_time: float = Field(
        ..., description="Average response time in milliseconds"
    )
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate (0-1)")
    throughput: float = Field(..., description="Requests per second")
    p95_response_time: float = Field(..., description="95th percentile response time")
    p99_response_time: float = Field(..., description="99th percentile response time")


class AlertDefinition(BaseModel):
    """Alert definition model."""

    alert_id: str = Field(..., description="Unique alert identifier")
    name: str = Field(..., description="Alert name")
    description: str = Field(..., description="Alert description")
    condition: str = Field(..., description="Alert condition")
    severity: str = Field(
        ..., regex="^(low|medium|high|critical)$", description="Alert severity"
    )
    enabled: bool = Field(True, description="Whether alert is enabled")
    notification_channels: list[str] = Field(
        default_factory=list, description="Notification channels"
    )


# Multi-Agent Coordination Models
class AgentCapability(BaseModel):
    """Agent capability description."""

    capability_id: str = Field(..., description="Unique capability identifier")
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    input_schema: dict[str, Any] = Field(
        ..., description="Input schema for the capability"
    )
    output_schema: dict[str, Any] = Field(
        ..., description="Output schema for the capability"
    )


class AgentRegistration(BaseModel):
    """Agent registration model."""

    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Agent type")
    capabilities: list[AgentCapability] = Field(..., description="Agent capabilities")
    endpoint: str = Field(..., description="Agent communication endpoint")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Agent metadata")


class TaskRequest(BaseRequest):
    """Task request for agent coordination."""

    task_type: str = Field(..., description="Type of task to execute")
    parameters: dict[str, Any] = Field(..., description="Task parameters")
    priority: MessagePriorities = Field(
        MessagePriorities.NORMAL, description="Task priority"
    )
    timeout: int | None = Field(None, description="Task timeout in seconds")
    required_capabilities: list[str] = Field(
        default_factory=list, description="Required agent capabilities"
    )


class TaskResponse(BaseResponse):
    """Task execution response."""

    task_id: str = Field(..., description="Task identifier")
    result: dict[str, Any] = Field(..., description="Task execution result")
    execution_time: float = Field(..., description="Task execution time in seconds")
    agent_id: str = Field(..., description="Agent that executed the task")


# Batch Operation Models
class BatchRequest(BaseRequest):
    """Batch operation request."""

    operations: list[dict[str, Any]] = Field(
        ..., description="List of operations to execute"
    )
    fail_fast: bool = Field(False, description="Whether to stop on first failure")
    parallel: bool = Field(
        True, description="Whether to execute operations in parallel"
    )

    @validator("operations")
    def validate_operations_not_empty(cls, v):
        """Ensure operations list is not empty."""
        if not v:
            raise ValueError("Operations list cannot be empty")
        return v


class BatchResponse(BaseResponse):
    """Batch operation response."""

    results: list[dict[str, Any]] = Field(..., description="Results for each operation")
    successful_operations: int = Field(
        ..., description="Number of successful operations"
    )
    failed_operations: int = Field(..., description="Number of failed operations")
    execution_time: float = Field(..., description="Total execution time in seconds")


# Configuration Models
class ServiceConfiguration(BaseModel):
    """Service configuration model."""

    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: EnvironmentTypes = Field(..., description="Environment type")
    config_data: dict[str, Any] = Field(..., description="Configuration data")
    last_updated: datetime = Field(..., description="Last update timestamp")
    config_version: str = Field(..., description="Configuration version")


class FeatureFlag(BaseModel):
    """Feature flag model."""

    flag_name: str = Field(..., description="Feature flag name")
    enabled: bool = Field(..., description="Whether feature is enabled")
    description: str = Field(..., description="Feature description")
    environment: EnvironmentTypes | None = Field(
        None, description="Environment restriction"
    )
    user_percentage: float = Field(
        100.0, ge=0.0, le=100.0, description="Percentage of users for gradual rollout"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


# Event and Audit Models
class AuditEvent(BaseModel):
    """Audit event model."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: str | None = Field(None, description="User who triggered the event")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: str = Field(..., description="Identifier of affected resource")
    action: str = Field(..., description="Action performed")
    outcome: str = Field(..., description="Event outcome (success/failure)")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional event details"
    )
    ip_address: str | None = Field(
        None, regex=PATTERNS["IP_ADDRESS"], description="Client IP address"
    )


class EventStreamRequest(BaseRequest):
    """Event stream subscription request."""

    event_types: list[str] = Field(..., description="Event types to subscribe to")
    filters: dict[str, Any] = Field(default_factory=dict, description="Event filters")
    start_time: datetime | None = Field(
        None, description="Start time for historical events"
    )


# Data Transfer Models
class DataExportRequest(BaseRequest):
    """Data export request."""

    export_type: str = Field(..., description="Type of data to export")
    format: str = Field("json", regex="^(json|csv|xml)$", description="Export format")
    filters: dict[str, Any] = Field(default_factory=dict, description="Data filters")
    include_metadata: bool = Field(True, description="Whether to include metadata")


class DataImportRequest(BaseRequest):
    """Data import request."""

    import_type: str = Field(..., description="Type of data to import")
    data: list[dict[str, Any]] | str = Field(..., description="Data to import")
    validation_mode: str = Field(
        "strict", regex="^(strict|permissive)$", description="Validation mode"
    )
    overwrite_existing: bool = Field(
        False, description="Whether to overwrite existing data"
    )


# Integration Models
class WebhookRequest(BaseModel):
    """Webhook request model."""

    webhook_id: str = Field(..., description="Webhook identifier")
    event_type: str = Field(..., description="Event type that triggered webhook")
    payload: dict[str, Any] = Field(..., description="Webhook payload")
    timestamp: datetime = Field(..., description="Event timestamp")
    signature: str | None = Field(
        None, description="Webhook signature for verification"
    )


class ExternalAPIRequest(BaseRequest):
    """External API integration request."""

    api_name: str = Field(..., description="External API name")
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(
        ..., regex="^(GET|POST|PUT|PATCH|DELETE)$", description="HTTP method"
    )
    headers: dict[str, str] = Field(default_factory=dict, description="Request headers")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Request parameters"
    )


# Custom Validation Models
class ValidationRule(BaseModel):
    """Custom validation rule."""

    rule_id: str = Field(..., description="Unique rule identifier")
    field_name: str = Field(..., description="Field to validate")
    rule_type: str = Field(..., description="Type of validation rule")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Rule parameters"
    )
    error_message: str = Field(..., description="Error message for validation failure")
    enabled: bool = Field(True, description="Whether rule is enabled")


class ValidationRequest(BaseRequest):
    """Data validation request."""

    data: dict[str, Any] = Field(..., description="Data to validate")
    schema_name: str = Field(..., description="Validation schema name")
    strict_mode: bool = Field(True, description="Whether to use strict validation")
    custom_rules: list[ValidationRule] = Field(
        default_factory=list, description="Additional custom rules"
    )


class ValidationResponse(BaseResponse):
    """Data validation response."""

    is_valid: bool = Field(..., description="Whether data is valid")
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Validation errors"
    )
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    validated_data: dict[str, Any] | None = Field(
        None, description="Cleaned/validated data"
    )
