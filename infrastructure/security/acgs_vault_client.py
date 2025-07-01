#!/usr/bin/env python3
"""
ACGS Vault Client Integration
Service-specific Vault client for secure secrets management across all ACGS services.
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import hvac
from prometheus_client import CollectorRegistry, Counter, Histogram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ServiceVaultConfig:
    """Vault configuration for ACGS services."""

    service_name: str
    vault_url: str = "http://localhost:8200"
    vault_role_id: str | None = None
    vault_secret_id: str | None = None
    vault_token: str | None = None

    # Service-specific configuration
    kv_mount_point: str = "acgs-secrets"
    database_mount_point: str = "acgs-database"
    pki_mount_point: str = "acgs-pki"

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    enable_constitutional_validation: bool = True


class ACGSVaultClient:
    """ACGS service Vault client."""

    def __init__(self, config: ServiceVaultConfig):
        self.config = config
        self.client: hvac.Client | None = None

        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # Cache for frequently accessed secrets
        self.secret_cache: dict[str, dict] = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info(f"ACGS Vault Client initialized for {config.service_name}")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.vault_requests = Counter(
            "acgs_vault_requests_total",
            "Total Vault requests by service",
            ["service", "operation", "status"],
            registry=self.registry,
        )

        self.vault_request_duration = Histogram(
            "acgs_vault_request_duration_seconds",
            "Duration of Vault requests",
            ["service", "operation"],
            registry=self.registry,
        )

        self.constitutional_validations = Counter(
            "acgs_vault_constitutional_validations_total",
            "Constitutional compliance validations",
            ["service", "status"],
            registry=self.registry,
        )

    async def initialize(self):
        """Initialize Vault client."""
        logger.info(f"Initializing Vault client for {self.config.service_name}")

        try:
            # Create Vault client
            self.client = hvac.Client(url=self.config.vault_url)

            # Authenticate
            await self.authenticate()

            # Validate constitutional compliance
            if self.config.enable_constitutional_validation:
                await self.validate_constitutional_compliance()

            logger.info(f"Vault client initialized for {self.config.service_name}")

        except Exception as e:
            logger.error(
                f"Failed to initialize Vault client for {self.config.service_name}: {e}"
            )
            raise

    async def authenticate(self):
        """Authenticate with Vault using AppRole or token."""
        try:
            if self.config.vault_token:
                # Use token authentication
                self.client.token = self.config.vault_token

            elif self.config.vault_role_id and self.config.vault_secret_id:
                # Use AppRole authentication
                auth_response = self.client.auth.approle.login(
                    role_id=self.config.vault_role_id,
                    secret_id=self.config.vault_secret_id,
                )
                self.client.token = auth_response["auth"]["client_token"]

            else:
                # Try environment variables
                vault_token = os.getenv("VAULT_TOKEN")
                vault_role_id = os.getenv("VAULT_ROLE_ID")
                vault_secret_id = os.getenv("VAULT_SECRET_ID")

                if vault_token:
                    self.client.token = vault_token
                elif vault_role_id and vault_secret_id:
                    auth_response = self.client.auth.approle.login(
                        role_id=vault_role_id, secret_id=vault_secret_id
                    )
                    self.client.token = auth_response["auth"]["client_token"]
                else:
                    raise ValueError("No Vault authentication method available")

            # Verify authentication
            if not self.client.is_authenticated():
                raise RuntimeError("Failed to authenticate with Vault")

            logger.info(
                f"Successfully authenticated {self.config.service_name} with Vault"
            )

        except Exception as e:
            logger.error(
                f"Failed to authenticate {self.config.service_name} with Vault: {e}"
            )
            raise

    async def validate_constitutional_compliance(self):
        """Validate constitutional compliance."""
        start_time = time.time()

        try:
            # Retrieve constitutional hash from Vault
            constitutional_secret = await self.get_secret("constitutional/hash")

            if not constitutional_secret:
                raise ValueError("Constitutional hash not found in Vault")

            stored_hash = constitutional_secret.get("value")

            if stored_hash != CONSTITUTIONAL_HASH:
                self.constitutional_validations.labels(
                    service=self.config.service_name, status="failed"
                ).inc()
                raise ValueError(
                    f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, got {stored_hash}"
                )

            self.constitutional_validations.labels(
                service=self.config.service_name, status="passed"
            ).inc()

            logger.debug(
                f"Constitutional compliance validated for {self.config.service_name}"
            )

        except Exception as e:
            self.constitutional_validations.labels(
                service=self.config.service_name, status="error"
            ).inc()
            logger.error(
                f"Constitutional compliance validation failed for {self.config.service_name}: {e}"
            )
            raise

    async def get_secret(
        self, secret_path: str, use_cache: bool = True
    ) -> dict[str, Any] | None:
        """Get a secret from Vault."""
        start_time = time.time()

        try:
            # Check cache first
            if use_cache and secret_path in self.secret_cache:
                cached_secret = self.secret_cache[secret_path]
                if time.time() - cached_secret["cached_at"] < self.cache_ttl:
                    logger.debug(
                        f"Retrieved {secret_path} from cache for {self.config.service_name}"
                    )
                    return cached_secret["data"]

            # Retrieve from Vault
            response = self.client.secrets.kv.v2.read_secret_version(
                path=secret_path, mount_point=self.config.kv_mount_point
            )

            secret_data = response["data"]["data"]

            # Remove metadata if present
            if "_metadata" in secret_data:
                del secret_data["_metadata"]

            # Cache the secret
            if use_cache:
                self.secret_cache[secret_path] = {
                    "data": secret_data,
                    "cached_at": time.time(),
                }

            # Record metrics
            self.vault_requests.labels(
                service=self.config.service_name,
                operation="get_secret",
                status="success",
            ).inc()

            self.vault_request_duration.labels(
                service=self.config.service_name, operation="get_secret"
            ).observe(time.time() - start_time)

            logger.debug(
                f"Retrieved secret {secret_path} for {self.config.service_name}"
            )
            return secret_data

        except Exception as e:
            self.vault_requests.labels(
                service=self.config.service_name, operation="get_secret", status="error"
            ).inc()

            logger.error(
                f"Failed to get secret {secret_path} for {self.config.service_name}: {e}"
            )
            return None

    async def get_database_credentials(
        self, role_name: str | None = None
    ) -> dict[str, str] | None:
        """Get dynamic database credentials."""
        start_time = time.time()

        try:
            if not role_name:
                role_name = f"{self.config.service_name.replace('-', '_')}_role"

            # Generate dynamic credentials
            response = self.client.secrets.database.generate_credentials(
                name=role_name, mount_point=self.config.database_mount_point
            )

            credentials = response["data"]

            # Record metrics
            self.vault_requests.labels(
                service=self.config.service_name,
                operation="get_database_credentials",
                status="success",
            ).inc()

            self.vault_request_duration.labels(
                service=self.config.service_name, operation="get_database_credentials"
            ).observe(time.time() - start_time)

            logger.info(
                f"Generated database credentials for {self.config.service_name}"
            )
            return credentials

        except Exception as e:
            self.vault_requests.labels(
                service=self.config.service_name,
                operation="get_database_credentials",
                status="error",
            ).inc()

            logger.error(
                f"Failed to get database credentials for {self.config.service_name}: {e}"
            )
            return None

    async def get_certificate(
        self, common_name: str | None = None, role_name: str = "service-cert"
    ) -> dict[str, str] | None:
        """Get a TLS certificate from Vault PKI."""
        start_time = time.time()

        try:
            if not common_name:
                common_name = f"{self.config.service_name}.acgs.local"

            # Generate certificate
            response = self.client.secrets.pki.generate_certificate(
                name=role_name,
                common_name=common_name,
                mount_point=self.config.pki_mount_point,
            )

            certificate_data = response["data"]

            # Record metrics
            self.vault_requests.labels(
                service=self.config.service_name,
                operation="get_certificate",
                status="success",
            ).inc()

            self.vault_request_duration.labels(
                service=self.config.service_name, operation="get_certificate"
            ).observe(time.time() - start_time)

            logger.info(f"Generated certificate for {self.config.service_name}")
            return certificate_data

        except Exception as e:
            self.vault_requests.labels(
                service=self.config.service_name,
                operation="get_certificate",
                status="error",
            ).inc()

            logger.error(
                f"Failed to get certificate for {self.config.service_name}: {e}"
            )
            return None

    async def store_secret(self, secret_path: str, secret_data: dict[str, Any]) -> bool:
        """Store a secret in Vault (if service has write permissions)."""
        start_time = time.time()

        try:
            # Add service metadata
            secret_with_metadata = {
                **secret_data,
                "_metadata": {
                    "created_by": self.config.service_name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            }

            # Store in Vault
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,
                secret=secret_with_metadata,
                mount_point=self.config.kv_mount_point,
            )

            # Invalidate cache
            if secret_path in self.secret_cache:
                del self.secret_cache[secret_path]

            # Record metrics
            self.vault_requests.labels(
                service=self.config.service_name,
                operation="store_secret",
                status="success",
            ).inc()

            self.vault_request_duration.labels(
                service=self.config.service_name, operation="store_secret"
            ).observe(time.time() - start_time)

            logger.info(f"Stored secret {secret_path} from {self.config.service_name}")
            return True

        except Exception as e:
            self.vault_requests.labels(
                service=self.config.service_name,
                operation="store_secret",
                status="error",
            ).inc()

            logger.error(
                f"Failed to store secret {secret_path} from {self.config.service_name}: {e}"
            )
            return False

    async def get_service_config(self) -> dict[str, Any]:
        """Get service-specific configuration from Vault."""
        try:
            service_config_path = f"{self.config.service_name}/config"
            config_data = await self.get_secret(service_config_path)

            if not config_data:
                # Return default configuration
                return self.get_default_service_config()

            return config_data

        except Exception as e:
            logger.warning(
                f"Failed to get service config for {self.config.service_name}: {e}"
            )
            return self.get_default_service_config()

    def get_default_service_config(self) -> dict[str, Any]:
        """Get default service configuration."""
        return {
            "service_name": self.config.service_name,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "vault_integration": True,
            "metrics_enabled": True,
            "log_level": "INFO",
            "health_check_interval": 30,
            "constitutional_validation_interval": 300,
        }

    async def renew_token(self) -> bool:
        """Renew Vault token if possible."""
        try:
            if self.client.token:
                self.client.auth.token.renew_self()
                logger.info(f"Renewed Vault token for {self.config.service_name}")
                return True
            return False

        except Exception as e:
            logger.warning(
                f"Failed to renew Vault token for {self.config.service_name}: {e}"
            )
            return False

    def clear_cache(self):
        """Clear the secret cache."""
        self.secret_cache.clear()
        logger.info(f"Cleared secret cache for {self.config.service_name}")

    def get_client_status(self) -> dict[str, Any]:
        """Get Vault client status."""
        try:
            return {
                "service_name": self.config.service_name,
                "vault_url": self.config.vault_url,
                "authenticated": (
                    self.client.is_authenticated() if self.client else False
                ),
                "cached_secrets": len(self.secret_cache),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "service_name": self.config.service_name,
                "vault_url": self.config.vault_url,
                "authenticated": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Service-specific Vault client factory
def create_vault_client(service_name: str, **kwargs) -> ACGSVaultClient:
    """Create a Vault client for a specific ACGS service."""
    config = ServiceVaultConfig(service_name=service_name, **kwargs)
    return ACGSVaultClient(config)


# Pre-configured clients for ACGS services
def create_auth_service_vault_client(**kwargs) -> ACGSVaultClient:
    """Create Vault client for Auth Service."""
    return create_vault_client("auth-service", **kwargs)


def create_ac_service_vault_client(**kwargs) -> ACGSVaultClient:
    """Create Vault client for Algorithmic Constitution Service."""
    return create_vault_client("ac-service", **kwargs)


def create_integrity_service_vault_client(**kwargs) -> ACGSVaultClient:
    """Create Vault client for Integrity Verification Service."""
    return create_vault_client("integrity-service", **kwargs)


def create_fv_service_vault_client(**kwargs) -> ACGSVaultClient:
    """Create Vault client for Formal Verification Service."""
    return create_vault_client("fv-service", **kwargs)


def create_gs_service_vault_client(**kwargs) -> ACGSVaultClient:
    """Create Vault client for Governance Simulation Service."""
    return create_vault_client("gs-service", **kwargs)


def create_pgc_service_vault_client(**kwargs) -> ACGSVaultClient:
    """Create Vault client for Policy Generation Consensus Service."""
    return create_vault_client("pgc-service", **kwargs)


def create_ec_service_vault_client(**kwargs) -> ACGSVaultClient:
    """Create Vault client for Evolutionary Computation Service."""
    return create_vault_client("ec-service", **kwargs)


# Example usage and testing
if __name__ == "__main__":

    async def test_vault_client():
        # Test with auth service
        auth_client = create_auth_service_vault_client()

        try:
            await auth_client.initialize()

            # Test getting a secret
            config = await auth_client.get_service_config()
            print(f"Auth service config: {config}")

            # Test getting database credentials
            db_creds = await auth_client.get_database_credentials()
            if db_creds:
                print(
                    f"Database credentials generated: username={db_creds.get('username')}"
                )

            # Test constitutional compliance
            constitutional_secret = await auth_client.get_secret("constitutional/hash")
            if constitutional_secret:
                print(
                    f"Constitutional hash validated: {constitutional_secret.get('value')}"
                )

            # Get client status
            status = auth_client.get_client_status()
            print(f"Client status: {status}")

        except Exception as e:
            print(f"Test failed: {e}")

    asyncio.run(test_vault_client())
