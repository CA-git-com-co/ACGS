"""
Advanced Configuration Management for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Centralized configuration with environment support, validation, and hot reloading.
"""

from .config_manager import (
    ConfigManager,
    ConfigSchema,
    ConfigValidator,
    EnvironmentConfig,
    get_config_manager,
)
from .feature_flags import (
    FeatureFlag,
    FeatureFlagCondition,
    FeatureFlagManager,
    UserContext,
    get_feature_flag_manager,
)
from .secrets_manager import (
    EnvironmentSecretsProvider,
    SecretProvider,
    SecretsManager,
    VaultSecretsProvider,
    get_secrets_manager,
)
from .settings import (
    CacheSettings,
    DatabaseSettings,
    LoggingSettings,
    SecuritySettings,
    Settings,
    get_settings,
)

__all__ = [
    # Configuration Management
    "ConfigManager",
    "ConfigSchema",
    "ConfigValidator",
    "EnvironmentConfig",
    "get_config_manager",
    # Feature Flags
    "FeatureFlagManager",
    "FeatureFlag",
    "FeatureFlagCondition",
    "UserContext",
    "get_feature_flag_manager",
    # Secrets Management
    "SecretsManager",
    "SecretProvider",
    "EnvironmentSecretsProvider",
    "VaultSecretsProvider",
    "get_secrets_manager",
    # Settings
    "Settings",
    "DatabaseSettings",
    "CacheSettings",
    "LoggingSettings",
    "SecuritySettings",
    "get_settings",
]
