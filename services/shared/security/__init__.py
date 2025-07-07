"""
Enhanced Security Module for ACGS

This module provides comprehensive security capabilities including:
- Unified input validation and sanitization
- XSS and SQL injection prevention
- CSRF protection
- File upload security
- Rate limiting and middleware
"""

# Constitutional Hash: cdd01ef066bc6cf2

from .auth_security_integration import (
    AuthSecurityIntegration,
    create_auth_security_integration,
    validate_user_input_secure,
)
from .csrf_protection import (
    CSRF_JAVASCRIPT_SNIPPET,
    CSRFConfig,
    CSRFMethod,
    CSRFProtection,
    CSRFProtectionMiddleware,
    CSRFTokenManager,
    create_csrf_protection,
    generate_csrf_meta_tag,
    get_csrf_headers,
)
from .enhanced_audit_logging import (
    AuditEvent,
    AuditEventType,
    AuditLevel,
    ComplianceFramework,
    EnhancedAuditLogger,
    FileAuditStorage,
    create_audit_logger,
    log_user_action,
)
from .enhanced_encryption import (
    DecryptionResult,
    EncryptionAlgorithm,
    EncryptionKey,
    EncryptionResult,
    EnhancedEncryptionManager,
    FileKeyStore,
    KeyType,
    KeyUsage,
    create_encryption_manager,
    derive_key_from_password,
    encrypt_constitutional_data,
    generate_secure_password,
)
from .enhanced_rbac import (
    ActionType,
    EnhancedRBACManager,
    Permission,
    PermissionEvaluationContext,
    PermissionLevel,
    ResourceType,
    Role,
    UserPermissions,
    check_user_permission,
    create_permission,
)
from .security_config_helper import (
    ACGSSecurityConfigHelper,
    ServiceSecurityProfile,
    ServiceType,
    create_custom_service_security,
    get_auth_service_security,
    get_constitutional_ai_security,
    get_platform_service_security,
)
from .unified_input_validation import (
    EnhancedInputValidator,
    SecureBaseModel,
    SecureEmailRequest,
    SecureLoginRequest,
    SecureStringField,
    SecurityConfig,
    SecurityLevel,
    SecurityMiddleware,
    ValidationResult,
    create_security_middleware,
    sanitize_dict,
    validate_input_secure,
)

__all__ = [
    "EnhancedInputValidator",
    "SecurityMiddleware",
    "SecurityConfig",
    "SecurityLevel",
    "ValidationResult",
    "SecureBaseModel",
    "SecureLoginRequest",
    "SecureEmailRequest",
    "SecureStringField",
    "create_security_middleware",
    "validate_input_secure",
    "sanitize_dict",
    "CSRFProtection",
    "CSRFProtectionMiddleware",
    "CSRFConfig",
    "CSRFTokenManager",
    "CSRFMethod",
    "create_csrf_protection",
    "generate_csrf_meta_tag",
    "get_csrf_headers",
    "CSRF_JAVASCRIPT_SNIPPET",
    "AuthSecurityIntegration",
    "create_auth_security_integration",
    "validate_user_input_secure",
    "EnhancedRBACManager",
    "Permission",
    "Role",
    "UserPermissions",
    "PermissionEvaluationContext",
    "PermissionLevel",
    "ResourceType",
    "ActionType",
    "check_user_permission",
    "create_permission",
    "EnhancedAuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditLevel",
    "ComplianceFramework",
    "FileAuditStorage",
    "create_audit_logger",
    "log_user_action",
    "ACGSSecurityConfigHelper",
    "ServiceType",
    "ServiceSecurityProfile",
    "get_auth_service_security",
    "get_constitutional_ai_security",
    "get_platform_service_security",
    "create_custom_service_security",
    "EnhancedEncryptionManager",
    "EncryptionKey",
    "EncryptionResult",
    "DecryptionResult",
    "EncryptionAlgorithm",
    "KeyType",
    "KeyUsage",
    "FileKeyStore",
    "create_encryption_manager",
    "encrypt_constitutional_data",
    "generate_secure_password",
    "derive_key_from_password",
]
