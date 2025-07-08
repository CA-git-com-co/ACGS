"""
ACGS Shared Constants and Enums
Constitutional Hash: cdd01ef066bc6cf2

This module centralizes all magic numbers, strings, and configuration constants
used throughout the ACGS system to improve maintainability and type safety.
"""

from enum import Enum, IntEnum
from typing import Final

# Constitutional compliance
CONSTITUTIONAL_HASH: Final[str] = "cdd01ef066bc6cf2"

# Service identification
SERVICE_VERSION: Final[str] = "3.0.0"
SERVICE_USER_AGENT: Final[str] = "ACGS-ServiceMesh/1.0"


# Default port assignments
class ServicePorts(IntEnum):
    """Standardized port assignments for ACGS services."""

    # Core Services
    AUTH_SERVICE = 8000
    CONSTITUTIONAL_AI = 8001
    INTEGRITY_SERVICE = 8002
    GOVERNANCE_SYNTHESIS = 8003
    POLICY_GOVERNANCE = 8004
    FORMAL_VERIFICATION = 8005
    EVOLUTIONARY_COMPUTATION = 8006
    CODE_ANALYSIS = 8007

    # Coordination Services
    MULTI_AGENT_COORDINATOR = 8008
    WORKER_AGENTS = 8009
    BLACKBOARD_SERVICE = 8010

    # Infrastructure Services
    API_GATEWAY = 8015
    AUTH_LEGACY = 8016

    # Database and Cache
    POSTGRES_DEFAULT = 5439
    REDIS_DEFAULT = 6389

    # Monitoring
    PROMETHEUS_METRICS = 9090


class TimeoutValues(IntEnum):
    """Standard timeout values in seconds."""

    # HTTP timeouts
    HTTP_CONNECT_TIMEOUT = 5
    HTTP_READ_TIMEOUT = 30
    HTTP_WRITE_TIMEOUT = 30
    HTTP_TOTAL_TIMEOUT = 60

    # Database timeouts
    DB_QUERY_TIMEOUT = 30
    DB_CONNECTION_TIMEOUT = 10
    DB_POOL_TIMEOUT = 30

    # Cache timeouts
    CACHE_SHORT_TTL = 300  # 5 minutes
    CACHE_MEDIUM_TTL = 1800  # 30 minutes
    CACHE_LONG_TTL = 3600  # 1 hour
    CACHE_VERY_LONG_TTL = 86400  # 24 hours

    # Authentication timeouts
    JWT_ACCESS_TOKEN_MINUTES = 30
    JWT_REFRESH_TOKEN_DAYS = 7
    JWT_RESET_TOKEN_MINUTES = 15

    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # 1 minute
    RATE_LIMIT_MAX_REQUESTS = 100

    # Circuit breaker
    CIRCUIT_BREAKER_TIMEOUT = 60
    CIRCUIT_BREAKER_THRESHOLD = 5


class HttpStatusCodes(IntEnum):
    """Common HTTP status codes for consistent usage."""

    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server Errors
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class DatabaseConfig(Enum):
    """Database configuration constants."""

    # Connection pool settings
    MIN_POOL_SIZE = 5
    MAX_POOL_SIZE = 20
    POOL_TIMEOUT = 30

    # Query settings
    DEFAULT_LIMIT = 100
    MAX_LIMIT = 1000

    # Pagination
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 500


class RedisConfig(Enum):
    """Redis configuration constants."""

    # Connection settings
    MAX_CONNECTIONS = 50
    CONNECTION_TIMEOUT = 5
    DEFAULT_DB = 0

    # Key prefixes
    CACHE_PREFIX = "acgs:cache"
    SESSION_PREFIX = "acgs:session"
    LOCK_PREFIX = "acgs:lock"
    QUEUE_PREFIX = "acgs:queue"


class SecurityConfig(Enum):
    """Security configuration constants."""

    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    # JWT settings
    JWT_ALGORITHM = "HS256"
    MIN_SECRET_KEY_LENGTH = 32

    # Rate limiting
    DEFAULT_RATE_LIMIT = 100
    STRICT_RATE_LIMIT = 10
    BURST_RATE_LIMIT = 200

    # Session settings
    MAX_ACTIVE_SESSIONS = 5
    SESSION_CLEANUP_INTERVAL = 3600  # 1 hour


class LogLevel(Enum):
    """Logging levels for consistent usage."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ContentTypes(Enum):
    """Standard content types."""

    JSON = "application/json"
    XML = "application/xml"
    HTML = "text/html"
    PLAIN_TEXT = "text/plain"
    FORM_DATA = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"


class HeaderNames(Enum):
    """Standard HTTP header names."""

    AUTHORIZATION = "Authorization"
    CONTENT_TYPE = "Content-Type"
    USER_AGENT = "User-Agent"
    X_REQUEST_ID = "X-Request-ID"
    X_CONSTITUTIONAL_HASH = "X-Constitutional-Hash"
    X_SERVICE_NAME = "X-Service-Name"
    X_SERVICE_VERSION = "X-Service-Version"
    X_TENANT_ID = "X-Tenant-ID"
    X_USER_ID = "X-User-ID"


class ErrorCodes(Enum):
    """Application-specific error codes."""

    # Authentication errors
    INVALID_CREDENTIALS = "AUTH_001"
    TOKEN_EXPIRED = "AUTH_002"
    TOKEN_INVALID = "AUTH_003"
    INSUFFICIENT_PERMISSIONS = "AUTH_004"

    # Validation errors
    INVALID_INPUT = "VAL_001"
    MISSING_REQUIRED_FIELD = "VAL_002"
    INVALID_FORMAT = "VAL_003"
    VALUE_OUT_OF_RANGE = "VAL_004"

    # Service errors
    SERVICE_UNAVAILABLE = "SVC_001"
    SERVICE_TIMEOUT = "SVC_002"
    SERVICE_ERROR = "SVC_003"

    # Constitutional compliance errors
    CONSTITUTIONAL_HASH_MISMATCH = "CONST_001"
    COMPLIANCE_VIOLATION = "CONST_002"
    GOVERNANCE_VIOLATION = "CONST_003"


class FileExtensions(Enum):
    """Common file extensions."""

    PYTHON = ".py"
    JSON = ".json"
    YAML = ".yaml"
    YML = ".yml"
    TOML = ".toml"
    SQL = ".sql"
    LOG = ".log"
    CSV = ".csv"
    TXT = ".txt"


class EnvironmentTypes(Enum):
    """Environment types for configuration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class MessagePriorities(IntEnum):
    """Message queue priorities."""

    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class MetricsNames(Enum):
    """Standard metrics names for monitoring."""

    # Request metrics
    REQUEST_COUNT = "acgs_requests_total"
    REQUEST_DURATION = "acgs_request_duration_seconds"
    REQUEST_SIZE = "acgs_request_size_bytes"

    # Error metrics
    ERROR_COUNT = "acgs_errors_total"
    ERROR_RATE = "acgs_error_rate"

    # Database metrics
    DB_CONNECTION_COUNT = "acgs_db_connections_active"
    DB_QUERY_DURATION = "acgs_db_query_duration_seconds"

    # Cache metrics
    CACHE_HIT_RATE = "acgs_cache_hit_rate"
    CACHE_MISS_COUNT = "acgs_cache_misses_total"

    # Constitutional compliance metrics
    COMPLIANCE_SCORE = "acgs_compliance_score"
    CONSTITUTIONAL_VALIDATIONS = "acgs_constitutional_validations_total"


# Common regex patterns
PATTERNS = {
    "EMAIL": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "UUID": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    "JWT": r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$",
    "IP_ADDRESS": r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
    "CONSTITUTIONAL_HASH": r"^[a-f0-9]{16}$",
}

# Default messages
MESSAGES = {
    "UNAUTHORIZED": "Authentication required",
    "FORBIDDEN": "Insufficient permissions",
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Input validation failed",
    "SERVICE_ERROR": "Internal service error",
    "CONSTITUTIONAL_VIOLATION": "Constitutional compliance violation detected",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
}

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_METRICS": True,
    "ENABLE_TRACING": True,
    "ENABLE_CONSTITUTIONAL_VALIDATION": True,
    "ENABLE_RATE_LIMITING": True,
    "ENABLE_CIRCUIT_BREAKER": True,
    "ENABLE_CACHING": True,
}
