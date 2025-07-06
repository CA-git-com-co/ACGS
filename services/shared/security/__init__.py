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

from .unified_input_validation import (
    EnhancedInputValidator,
    SecurityMiddleware,
    SecurityConfig,
    SecurityLevel,
    ValidationResult,
    SecureBaseModel,
    SecureLoginRequest,
    SecureEmailRequest,
    SecureStringField,
    create_security_middleware,
    validate_input_secure,
    sanitize_dict,
)

from .csrf_protection import (
    CSRFProtection,
    CSRFProtectionMiddleware,
    CSRFConfig,
    CSRFTokenManager,
    CSRFMethod,
    create_csrf_protection,
    generate_csrf_meta_tag,
    get_csrf_headers,
    CSRF_JAVASCRIPT_SNIPPET,
)

from .auth_security_integration import (
    AuthSecurityIntegration,
    create_auth_security_integration,
    validate_user_input_secure,
)

from .enhanced_rbac import (
    EnhancedRBACManager,
    Permission,
    Role,
    UserPermissions,
    PermissionEvaluationContext,
    PermissionLevel,
    ResourceType,
    ActionType,
    check_user_permission,
    create_permission,
)

from .enhanced_audit_logging import (
    EnhancedAuditLogger,
    AuditEvent,
    AuditEventType,
    AuditLevel,
    ComplianceFramework,
    FileAuditStorage,
    create_audit_logger,
    log_user_action,
)

from .security_config_helper import (
    ACGSSecurityConfigHelper,
    ServiceType,
    ServiceSecurityProfile,
    get_auth_service_security,
    get_constitutional_ai_security,
    get_platform_service_security,
    create_custom_service_security,
)

from .enhanced_encryption import (
    EnhancedEncryptionManager,
    EncryptionKey,
    EncryptionResult,
    DecryptionResult,
    EncryptionAlgorithm,
    KeyType,
    KeyUsage,
    FileKeyStore,
    create_encryption_manager,
    encrypt_constitutional_data,
    generate_secure_password,
    derive_key_from_password,
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