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
    "CSRF_JAVASCRIPT_SNIPPET",
    "ACGSSecurityConfigHelper",
    "ActionType",
    "AuditEvent",
    "AuditEventType",
    "AuditLevel",
    "AuthSecurityIntegration",
    "CSRFConfig",
    "CSRFMethod",
    "CSRFProtection",
    "CSRFProtectionMiddleware",
    "CSRFTokenManager",
    "ComplianceFramework",
    "DecryptionResult",
    "EncryptionAlgorithm",
    "EncryptionKey",
    "EncryptionResult",
    "EnhancedAuditLogger",
    "EnhancedEncryptionManager",
    "EnhancedInputValidator",
    "EnhancedRBACManager",
    "FileAuditStorage",
    "FileKeyStore",
    "KeyType",
    "KeyUsage",
    "Permission",
    "PermissionEvaluationContext",
    "PermissionLevel",
    "ResourceType",
    "Role",
    "SecureBaseModel",
    "SecureEmailRequest",
    "SecureLoginRequest",
    "SecureStringField",
    "SecurityConfig",
    "SecurityLevel",
    "SecurityMiddleware",
    "ServiceSecurityProfile",
    "ServiceType",
    "UserPermissions",
    "ValidationResult",
    "check_user_permission",
    "create_audit_logger",
    "create_auth_security_integration",
    "create_csrf_protection",
    "create_custom_service_security",
    "create_encryption_manager",
    "create_permission",
    "create_security_middleware",
    "derive_key_from_password",
    "encrypt_constitutional_data",
    "generate_csrf_meta_tag",
    "generate_secure_password",
    "get_auth_service_security",
    "get_constitutional_ai_security",
    "get_csrf_headers",
    "get_platform_service_security",
    "log_user_action",
    "sanitize_dict",
    "validate_input_secure",
    "validate_user_input_secure",
]
