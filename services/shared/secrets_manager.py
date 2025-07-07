"""
ACGS Secrets Manager
Constitutional Hash: cdd01ef066bc6cf2

Secure secrets management for ACGS services.
"""

import logging
import os
import secrets
import string
from pathlib import Path
from typing import Any, Dict, Optional

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ACGSSecretsManager:
    """Secure secrets management for ACGS."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self._secrets_cache = {}

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variables."""
        try:
            value = os.getenv(key, default)
            if value:
                # Cache for performance (in production, use proper secret rotation)
                self._secrets_cache[key] = value
                logger.debug(f"Retrieved secret: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to retrieve secret {key}: {e}")
            return default

    def get_database_url(self) -> str:
        """Get database URL with fallback."""
        return self.get_secret("DATABASE_URL", "postgresql://localhost:5432/acgs")

    def get_redis_url(self) -> str:
        """Get Redis URL with fallback."""
        return self.get_secret("REDIS_URL", "redis://localhost:6379/0")

    def get_jwt_secret(self) -> str:
        """Get JWT secret key."""
        secret = self.get_secret("JWT_SECRET_KEY")
        if not secret:
            logger.warning("JWT_SECRET_KEY not set, using default (INSECURE)")
            return "default_jwt_secret_change_in_production"
        return secret

    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get API key for specific service."""
        key_name = f"{service_name.upper()}_API_KEY"
        return self.get_secret(key_name)

    def generate_secure_secret(self, length: int = 64) -> str:
        """Generate a cryptographically secure secret."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def generate_jwt_secret(self) -> str:
        """Generate a secure JWT secret key."""
        return self.generate_secure_secret(64)

    def generate_csrf_secret(self) -> str:
        """Generate a secure CSRF secret key."""
        return self.generate_secure_secret(32)

    def validate_secret_strength(
        self, secret: str, min_length: int = 32
    ) -> Dict[str, Any]:
        """Validate the strength of a secret."""
        issues = []

        if len(secret) < min_length:
            issues.append(f"Secret too short (minimum {min_length} characters)")

        if secret.lower() == secret or secret.upper() == secret:
            issues.append("Secret should contain mixed case")

        if not any(c.isdigit() for c in secret):
            issues.append("Secret should contain numbers")

        if not any(c in "!@#$%^&*" for c in secret):
            issues.append("Secret should contain special characters")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "length": len(secret),
            "constitutional_hash": self.constitutional_hash,
        }

    def validate_secrets_configuration(self) -> Dict[str, Any]:
        """Validate secrets configuration."""
        required_secrets = [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "DATABASE_URL",
        ]

        missing_secrets = []
        weak_secrets = []

        for secret_name in required_secrets:
            secret_value = self.get_secret(secret_name)
            if not secret_value:
                missing_secrets.append(secret_name)
            elif secret_name in ["SECRET_KEY", "JWT_SECRET_KEY"]:
                validation = self.validate_secret_strength(secret_value)
                if not validation["valid"]:
                    weak_secrets.append(
                        {"name": secret_name, "issues": validation["issues"]}
                    )

        return {
            "valid": len(missing_secrets) == 0 and len(weak_secrets) == 0,
            "missing_secrets": missing_secrets,
            "weak_secrets": weak_secrets,
            "constitutional_hash": self.constitutional_hash,
        }


# Global secrets manager instance
secrets_manager = ACGSSecretsManager()
