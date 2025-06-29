#!/usr/bin/env python3
"""
ACGS HashiCorp Vault Secrets Manager
Centralized secrets management with constitutional compliance and dynamic secrets.
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

import hvac
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class SecretMetadata:
    """Metadata for secrets stored in Vault."""
    secret_path: str
    secret_type: str  # static, dynamic, constitutional
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    # Access control
    allowed_services: List[str] = field(default_factory=list)
    required_policies: List[str] = field(default_factory=list)

@dataclass
class VaultConfiguration:
    """Vault configuration settings."""
    vault_url: str = "http://localhost:8200"
    vault_token: Optional[str] = None
    vault_role_id: Optional[str] = None
    vault_secret_id: Optional[str] = None
    
    # Mount points
    kv_mount_point: str = "acgs-secrets"
    database_mount_point: str = "acgs-database"
    pki_mount_point: str = "acgs-pki"
    
    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    enable_constitutional_validation: bool = True

class VaultSecretsManager:
    """HashiCorp Vault secrets manager for ACGS."""
    
    def __init__(self, config: VaultConfiguration):
        self.config = config
        self.client: Optional[hvac.Client] = None
        
        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()
        
        # Secret cache and metadata
        self.secret_metadata: Dict[str, SecretMetadata] = {}
        
        # Service configurations
        self.service_vault_policies = self.setup_service_policies()
        
        logger.info("Vault Secrets Manager initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for Vault operations."""
        self.secrets_accessed = Counter(
            'acgs_vault_secrets_accessed_total',
            'Total secrets accessed from Vault',
            ['secret_type', 'service', 'operation'],
            registry=self.registry
        )
        
        self.secrets_created = Counter(
            'acgs_vault_secrets_created_total',
            'Total secrets created in Vault',
            ['secret_type', 'service'],
            registry=self.registry
        )
        
        self.vault_operations_duration = Histogram(
            'acgs_vault_operations_duration_seconds',
            'Duration of Vault operations',
            ['operation', 'secret_type'],
            registry=self.registry
        )
        
        self.constitutional_compliance_checks = Counter(
            'acgs_vault_constitutional_compliance_checks_total',
            'Constitutional compliance checks for Vault operations',
            ['operation', 'compliance_status'],
            registry=self.registry
        )
        
        self.dynamic_secrets_issued = Counter(
            'acgs_vault_dynamic_secrets_issued_total',
            'Dynamic secrets issued by Vault',
            ['secret_engine', 'service'],
            registry=self.registry
        )

    def setup_service_policies(self) -> Dict[str, Dict]:
        """Setup Vault policies for each ACGS service."""
        return {
            "auth-service": {
                "policies": ["acgs-auth-policy"],
                "allowed_paths": [
                    "acgs-secrets/auth/*",
                    "acgs-database/creds/auth-role",
                    "acgs-pki/issue/auth-cert"
                ],
                "capabilities": ["read", "create", "update"]
            },
            
            "ac-service": {
                "policies": ["acgs-ac-policy"],
                "allowed_paths": [
                    "acgs-secrets/ac/*",
                    "acgs-secrets/constitutional/*",
                    "acgs-database/creds/ac-role"
                ],
                "capabilities": ["read", "create", "update"]
            },
            
            "integrity-service": {
                "policies": ["acgs-integrity-policy"],
                "allowed_paths": [
                    "acgs-secrets/integrity/*",
                    "acgs-database/creds/integrity-role"
                ],
                "capabilities": ["read"]
            },
            
            "fv-service": {
                "policies": ["acgs-fv-policy"],
                "allowed_paths": [
                    "acgs-secrets/fv/*",
                    "acgs-database/creds/fv-role"
                ],
                "capabilities": ["read"]
            },
            
            "gs-service": {
                "policies": ["acgs-gs-policy"],
                "allowed_paths": [
                    "acgs-secrets/gs/*",
                    "acgs-database/creds/gs-role"
                ],
                "capabilities": ["read", "create"]
            },
            
            "pgc-service": {
                "policies": ["acgs-pgc-policy"],
                "allowed_paths": [
                    "acgs-secrets/pgc/*",
                    "acgs-secrets/constitutional/*",
                    "acgs-database/creds/pgc-role"
                ],
                "capabilities": ["read", "create", "update"]
            },
            
            "ec-service": {
                "policies": ["acgs-ec-policy"],
                "allowed_paths": [
                    "acgs-secrets/ec/*",
                    "acgs-secrets/constitutional/*",
                    "acgs-database/creds/ec-role",
                    "acgs-pki/issue/ec-cert"
                ],
                "capabilities": ["read", "create", "update", "delete"]
            }
        }

    async def initialize(self):
        """Initialize Vault client and setup."""
        logger.info("Initializing Vault Secrets Manager...")
        
        # Create Vault client
        self.client = hvac.Client(url=self.config.vault_url)
        
        # Authenticate
        await self.authenticate()
        
        # Setup secret engines and policies
        await self.setup_vault_infrastructure()
        
        # Start metrics server
        start_http_server(8099, registry=self.registry)
        logger.info("Vault metrics server started on port 8099")
        
        logger.info("Vault Secrets Manager initialized successfully")

    async def authenticate(self):
        """Authenticate with Vault."""
        try:
            if self.config.vault_token:
                # Use token authentication
                self.client.token = self.config.vault_token
                
            elif self.config.vault_role_id and self.config.vault_secret_id:
                # Use AppRole authentication
                auth_response = self.client.auth.approle.login(
                    role_id=self.config.vault_role_id,
                    secret_id=self.config.vault_secret_id
                )
                self.client.token = auth_response['auth']['client_token']
                
            else:
                # Try to get token from environment
                vault_token = os.getenv('VAULT_TOKEN')
                if vault_token:
                    self.client.token = vault_token
                else:
                    raise ValueError("No Vault authentication method configured")
            
            # Verify authentication
            if not self.client.is_authenticated():
                raise RuntimeError("Failed to authenticate with Vault")
            
            logger.info("Successfully authenticated with Vault")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Vault: {e}")
            raise

    async def setup_vault_infrastructure(self):
        """Setup Vault secret engines, policies, and roles."""
        logger.info("Setting up Vault infrastructure...")
        
        try:
            # Enable secret engines
            await self.enable_secret_engines()
            
            # Create policies
            await self.create_vault_policies()
            
            # Setup database secrets engine
            await self.setup_database_secrets()
            
            # Setup PKI secrets engine
            await self.setup_pki_secrets()
            
            # Create constitutional compliance secrets
            await self.create_constitutional_secrets()
            
            logger.info("Vault infrastructure setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup Vault infrastructure: {e}")
            raise

    async def enable_secret_engines(self):
        """Enable required secret engines."""
        secret_engines = [
            (self.config.kv_mount_point, "kv-v2"),
            (self.config.database_mount_point, "database"),
            (self.config.pki_mount_point, "pki")
        ]
        
        for mount_point, engine_type in secret_engines:
            try:
                # Check if already enabled
                if mount_point in self.client.sys.list_mounted_secrets_engines()['data']:
                    logger.info(f"Secret engine {mount_point} already enabled")
                    continue
                
                # Enable secret engine
                self.client.sys.enable_secrets_engine(
                    backend_type=engine_type,
                    path=mount_point
                )
                logger.info(f"Enabled secret engine: {mount_point} ({engine_type})")
                
            except Exception as e:
                logger.warning(f"Failed to enable secret engine {mount_point}: {e}")

    async def create_vault_policies(self):
        """Create Vault policies for ACGS services."""
        for service_name, config in self.service_vault_policies.items():
            policy_name = config["policies"][0]
            
            # Generate policy document
            policy_rules = []
            for path in config["allowed_paths"]:
                capabilities = config["capabilities"]
                policy_rules.append(f'''
path "{path}" {{
    capabilities = {json.dumps(capabilities)}
}}''')
            
            # Add constitutional compliance validation
            policy_rules.append(f'''
path "acgs-secrets/constitutional/hash" {{
    capabilities = ["read"]
}}''')
            
            policy_document = "\n".join(policy_rules)
            
            try:
                self.client.sys.create_or_update_policy(
                    name=policy_name,
                    policy=policy_document
                )
                logger.info(f"Created/updated policy: {policy_name}")
                
            except Exception as e:
                logger.warning(f"Failed to create policy {policy_name}: {e}")

    async def setup_database_secrets(self):
        """Setup database secrets engine for dynamic credentials."""
        try:
            # Configure database connection
            db_config = {
                "plugin_name": "postgresql-database-plugin",
                "connection_url": "postgresql://{{username}}:{{password}}@localhost:5432/acgs?sslmode=disable",
                "allowed_roles": ["auth-role", "ac-role", "integrity-role", "fv-role", "gs-role", "pgc-role", "ec-role"],
                "username": "vault_admin",
                "password": "vault_admin_password"
            }
            
            self.client.secrets.database.configure(
                name="acgs-postgres",
                **db_config,
                mount_point=self.config.database_mount_point
            )
            
            # Create database roles for each service
            for service_name in self.service_vault_policies.keys():
                role_name = f"{service_name.replace('-', '_')}_role"
                
                creation_statements = [
                    f"CREATE ROLE \"{{{{name}}}}\" WITH LOGIN PASSWORD '{{{{password}}}}' VALID UNTIL '{{{{expiration}}}}';",
                    f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{{{name}}}}\";",
                    f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO \"{{{{name}}}}\";"
                ]
                
                self.client.secrets.database.create_role(
                    name=role_name,
                    db_name="acgs-postgres",
                    creation_statements=creation_statements,
                    default_ttl="1h",
                    max_ttl="24h",
                    mount_point=self.config.database_mount_point
                )
                
                logger.info(f"Created database role: {role_name}")
            
        except Exception as e:
            logger.warning(f"Failed to setup database secrets: {e}")

    async def setup_pki_secrets(self):
        """Setup PKI secrets engine for certificate management."""
        try:
            # Configure PKI root CA
            self.client.secrets.pki.generate_root(
                type="internal",
                common_name="ACGS Root CA",
                ttl="8760h",  # 1 year
                mount_point=self.config.pki_mount_point
            )
            
            # Configure PKI URLs
            self.client.secrets.pki.set_urls(
                issuing_certificates=[f"{self.config.vault_url}/v1/{self.config.pki_mount_point}/ca"],
                crl_distribution_points=[f"{self.config.vault_url}/v1/{self.config.pki_mount_point}/crl"],
                mount_point=self.config.pki_mount_point
            )
            
            # Create certificate roles
            cert_roles = ["auth-cert", "ec-cert", "service-cert"]
            
            for role_name in cert_roles:
                self.client.secrets.pki.create_or_update_role(
                    name=role_name,
                    allowed_domains=["acgs.local", "localhost"],
                    allow_subdomains=True,
                    max_ttl="720h",  # 30 days
                    mount_point=self.config.pki_mount_point
                )
                
                logger.info(f"Created PKI role: {role_name}")
            
        except Exception as e:
            logger.warning(f"Failed to setup PKI secrets: {e}")

    async def create_constitutional_secrets(self):
        """Create constitutional compliance secrets."""
        try:
            constitutional_secrets = {
                "hash": {
                    "value": CONSTITUTIONAL_HASH,
                    "description": "ACGS constitutional compliance hash",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                "validation_key": {
                    "value": "acgs_constitutional_validation_key_2024",
                    "description": "Key for constitutional validation operations",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            }
            
            for secret_name, secret_data in constitutional_secrets.items():
                await self.store_secret(
                    f"constitutional/{secret_name}",
                    secret_data,
                    secret_type="constitutional"
                )
            
            logger.info("Constitutional compliance secrets created")
            
        except Exception as e:
            logger.warning(f"Failed to create constitutional secrets: {e}")

    async def store_secret(
        self, 
        secret_path: str, 
        secret_data: Dict[str, Any],
        secret_type: str = "static",
        ttl: Optional[int] = None,
        allowed_services: Optional[List[str]] = None
    ) -> SecretMetadata:
        """Store a secret in Vault."""
        start_time = time.time()
        
        try:
            # Validate constitutional compliance
            if self.config.enable_constitutional_validation:
                await self.validate_constitutional_compliance("store_secret")
            
            # Add metadata to secret
            secret_with_metadata = {
                **secret_data,
                "_metadata": {
                    "secret_type": secret_type,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "allowed_services": allowed_services or [],
                    "ttl": ttl
                }
            }
            
            # Store in Vault
            full_path = f"{self.config.kv_mount_point}/data/{secret_path}"
            
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,
                secret=secret_with_metadata,
                mount_point=self.config.kv_mount_point
            )
            
            # Create metadata object
            metadata = SecretMetadata(
                secret_path=secret_path,
                secret_type=secret_type,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl) if ttl else None,
                allowed_services=allowed_services or []
            )
            
            self.secret_metadata[secret_path] = metadata
            
            # Record metrics
            self.secrets_created.labels(
                secret_type=secret_type,
                service="vault_manager"
            ).inc()
            
            self.vault_operations_duration.labels(
                operation="store_secret",
                secret_type=secret_type
            ).observe(time.time() - start_time)
            
            logger.info(f"Stored secret: {secret_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to store secret {secret_path}: {e}")
            raise

    async def retrieve_secret(
        self, 
        secret_path: str, 
        requesting_service: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a secret from Vault."""
        start_time = time.time()
        
        try:
            # Validate constitutional compliance
            if self.config.enable_constitutional_validation:
                await self.validate_constitutional_compliance("retrieve_secret")
            
            # Check access permissions
            if secret_path in self.secret_metadata:
                metadata = self.secret_metadata[secret_path]
                if metadata.allowed_services and requesting_service not in metadata.allowed_services:
                    raise PermissionError(f"Service {requesting_service} not allowed to access {secret_path}")
            
            # Retrieve from Vault
            response = self.client.secrets.kv.v2.read_secret_version(
                path=secret_path,
                mount_point=self.config.kv_mount_point
            )
            
            secret_data = response['data']['data']
            
            # Remove metadata from response
            if '_metadata' in secret_data:
                del secret_data['_metadata']
            
            # Update access tracking
            if secret_path in self.secret_metadata:
                self.secret_metadata[secret_path].access_count += 1
                self.secret_metadata[secret_path].last_accessed = datetime.now(timezone.utc)
            
            # Record metrics
            secret_type = self.secret_metadata.get(secret_path, SecretMetadata("", "unknown", datetime.now())).secret_type
            
            self.secrets_accessed.labels(
                secret_type=secret_type,
                service=requesting_service,
                operation="retrieve"
            ).inc()
            
            self.vault_operations_duration.labels(
                operation="retrieve_secret",
                secret_type=secret_type
            ).observe(time.time() - start_time)
            
            logger.debug(f"Retrieved secret: {secret_path} for service: {requesting_service}")
            return secret_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_path}: {e}")
            return None

    async def generate_dynamic_secret(
        self, 
        secret_engine: str, 
        role_name: str, 
        requesting_service: str
    ) -> Optional[Dict[str, Any]]:
        """Generate a dynamic secret."""
        start_time = time.time()
        
        try:
            # Validate constitutional compliance
            if self.config.enable_constitutional_validation:
                await self.validate_constitutional_compliance("generate_dynamic_secret")
            
            if secret_engine == "database":
                # Generate database credentials
                response = self.client.secrets.database.generate_credentials(
                    name=role_name,
                    mount_point=self.config.database_mount_point
                )
                
                credentials = response['data']
                
            elif secret_engine == "pki":
                # Generate certificate
                response = self.client.secrets.pki.generate_certificate(
                    name=role_name,
                    common_name=f"{requesting_service}.acgs.local",
                    mount_point=self.config.pki_mount_point
                )
                
                credentials = response['data']
                
            else:
                raise ValueError(f"Unsupported secret engine: {secret_engine}")
            
            # Record metrics
            self.dynamic_secrets_issued.labels(
                secret_engine=secret_engine,
                service=requesting_service
            ).inc()
            
            self.vault_operations_duration.labels(
                operation="generate_dynamic_secret",
                secret_type="dynamic"
            ).observe(time.time() - start_time)
            
            logger.info(f"Generated dynamic secret for {requesting_service} using {secret_engine}")
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to generate dynamic secret: {e}")
            return None

    async def validate_constitutional_compliance(self, operation: str):
        """Validate constitutional compliance for Vault operations."""
        try:
            # Retrieve constitutional hash from Vault
            stored_hash_response = self.client.secrets.kv.v2.read_secret_version(
                path="constitutional/hash",
                mount_point=self.config.kv_mount_point
            )
            
            stored_hash = stored_hash_response['data']['data']['value']
            
            if stored_hash != CONSTITUTIONAL_HASH:
                self.constitutional_compliance_checks.labels(
                    operation=operation,
                    compliance_status="failed"
                ).inc()
                raise ValueError(f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, got {stored_hash}")
            
            self.constitutional_compliance_checks.labels(
                operation=operation,
                compliance_status="passed"
            ).inc()
            
        except Exception as e:
            logger.error(f"Constitutional compliance validation failed for {operation}: {e}")
            self.constitutional_compliance_checks.labels(
                operation=operation,
                compliance_status="error"
            ).inc()
            raise

    async def rotate_secret(self, secret_path: str) -> bool:
        """Rotate a secret."""
        try:
            # This is a simplified rotation - in practice, you'd implement
            # service-specific rotation logic
            
            # Get current secret
            current_secret = await self.retrieve_secret(secret_path, "vault_manager")
            if not current_secret:
                return False
            
            # Generate new secret value (simplified)
            import secrets
            new_value = secrets.token_urlsafe(32)
            
            # Update secret
            updated_secret = {**current_secret, "value": new_value}
            await self.store_secret(secret_path, updated_secret)
            
            logger.info(f"Rotated secret: {secret_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate secret {secret_path}: {e}")
            return False

    def get_vault_status(self) -> Dict:
        """Get Vault status and health information."""
        try:
            health = self.client.sys.read_health_status()
            
            return {
                "vault_url": self.config.vault_url,
                "authenticated": self.client.is_authenticated(),
                "sealed": health.get("sealed", True),
                "standby": health.get("standby", False),
                "version": health.get("version", "unknown"),
                "cluster_name": health.get("cluster_name", "unknown"),
                "secrets_managed": len(self.secret_metadata),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get Vault status: {e}")
            return {
                "vault_url": self.config.vault_url,
                "authenticated": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# Global Vault manager instance
vault_config = VaultConfiguration()
vault_manager = VaultSecretsManager(vault_config)

if __name__ == "__main__":
    async def main():
        await vault_manager.initialize()
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Vault Secrets Manager...")
    
    asyncio.run(main())
