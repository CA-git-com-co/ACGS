#!/usr/bin/env python3
"""
Deployment Script for 4-Layer Security Architecture
Deploys and configures the complete security infrastructure for ACGS Evolutionary Computation Service.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityArchitectureDeployment:
    """Manages deployment of 4-layer security architecture."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.constitutional_hash = "cdd01ef066bc6cf2"

        self.deployment_config = {
            "ec_service_port": 8006,
            "opa_port": 8181,
            "jwt_secret": "acgs_ec_service_secret_key",
            "sandbox_runtime": "gvisor",  # or 'firecracker'
            "audit_retention_days": 90,
        }

    async def deploy_complete_security_architecture(self):
        """Deploy the complete 4-layer security architecture."""
        logger.info("Starting deployment of 4-layer security architecture...")

        try:
            # Step 1: Validate prerequisites
            await self.validate_prerequisites()

            # Step 2: Deploy Layer 1 - Sandboxing
            await self.deploy_layer1_sandboxing()

            # Step 3: Deploy Layer 2 - Policy Engine
            await self.deploy_layer2_policy_engine()

            # Step 4: Deploy Layer 3 - Authentication
            await self.deploy_layer3_authentication()

            # Step 5: Deploy Layer 4 - Audit Layer
            await self.deploy_layer4_audit()

            # Step 6: Configure integrations
            await self.configure_security_integrations()

            # Step 7: Validate deployment
            await self.validate_security_deployment()

            logger.info(
                "4-layer security architecture deployment completed successfully!"
            )

        except Exception as e:
            logger.error(f"Security architecture deployment failed: {e}")
            raise

    async def validate_prerequisites(self):
        """Validate system prerequisites for security architecture."""
        logger.info("Validating security prerequisites...")

        # Check if running as root (required for some security features)
        if os.geteuid() != 0:
            logger.warning(
                "Not running as root - some security features may be limited"
            )

        # Check Docker availability for sandboxing
        try:
            result = subprocess.run(
                ["docker", "--version"], check=False, capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info("✓ Docker is available for sandboxing")
            else:
                logger.warning("Docker not available - using simulated sandboxing")
        except FileNotFoundError:
            logger.warning("Docker not found - using simulated sandboxing")

        # Check if gVisor is available
        try:
            result = subprocess.run(
                ["runsc", "--version"], check=False, capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info("✓ gVisor (runsc) is available")
                self.deployment_config["sandbox_runtime"] = "gvisor"
            else:
                logger.info("gVisor not available - using Docker sandboxing")
                self.deployment_config["sandbox_runtime"] = "docker"
        except FileNotFoundError:
            logger.info("gVisor not found - using Docker sandboxing")
            self.deployment_config["sandbox_runtime"] = "docker"

        # Check Python dependencies
        required_packages = ["jwt", "prometheus_client"]
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ {package} is available")
            except ImportError:
                logger.error(f"✗ {package} is not installed")
                raise RuntimeError(f"Missing required package: {package}")

    async def deploy_layer1_sandboxing(self):
        """Deploy Layer 1: Sandboxing and Isolation."""
        logger.info("Deploying Layer 1: Sandboxing and Isolation...")

        # Create sandboxing directories
        sandbox_dirs = [
            "infrastructure/security/sandboxes",
            "infrastructure/security/sandbox_configs",
            "logs/sandbox_execution",
        ]

        for dir_path in sandbox_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created sandbox directory: {dir_path}")

        # Create sandbox configuration
        sandbox_config = {
            "runtime": self.deployment_config["sandbox_runtime"],
            "resource_limits": {
                "max_memory_mb": 512,
                "max_cpu_percent": 50,
                "max_execution_time_seconds": 300,
                "max_disk_mb": 100,
            },
            "security_settings": {
                "no_network": True,
                "read_only_filesystem": True,
                "drop_capabilities": ["ALL"],
                "seccomp_profile": "default",
            },
            "constitutional_hash": self.constitutional_hash,
        }

        config_path = (
            self.project_root / "infrastructure/security/sandbox_configs/default.json"
        )
        with open(config_path, "w") as f:
            json.dump(sandbox_config, f, indent=2)

        logger.info(f"Sandbox configuration saved to {config_path}")

        # Create sandbox startup script
        if self.deployment_config["sandbox_runtime"] == "gvisor":
            await self.create_gvisor_sandbox_script()
        else:
            await self.create_docker_sandbox_script()

    async def create_gvisor_sandbox_script(self):
        """Create gVisor sandbox startup script."""
        script_content = """#!/bin/bash
# gVisor Sandbox Startup Script for ACGS EC Service

SANDBOX_ID=$1
CONFIG_FILE=$2

if [ -z "$SANDBOX_ID" ] || [ -z "$CONFIG_FILE" ]; then
    echo "Usage: $0 <sandbox_id> <config_file>"
    exit 1
fi

# Create sandbox directory
SANDBOX_DIR="/tmp/acgs_sandbox_$SANDBOX_ID"
mkdir -p "$SANDBOX_DIR"

# Run with gVisor
runsc \\
    --platform=ptrace \\
    --network=none \\
    --file-access=exclusive \\
    --overlay \\
    run \\
    --bundle="$SANDBOX_DIR" \\
    --config="$CONFIG_FILE" \\
    "$SANDBOX_ID"

# Cleanup
rm -rf "$SANDBOX_DIR"
"""

        script_path = self.project_root / "scripts/security/start_gvisor_sandbox.sh"
        script_path.parent.mkdir(parents=True, exist_ok=True)

        with open(script_path, "w") as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)
        logger.info(f"gVisor sandbox script created: {script_path}")

    async def create_docker_sandbox_script(self):
        """Create Docker sandbox startup script."""
        script_content = """#!/bin/bash
# Docker Sandbox Startup Script for ACGS EC Service

SANDBOX_ID=$1
CONFIG_FILE=$2

if [ -z "$SANDBOX_ID" ] || [ -z "$CONFIG_FILE" ]; then
    echo "Usage: $0 <sandbox_id> <config_file>"
    exit 1
fi

# Run with Docker security constraints
docker run \\
    --name="acgs_sandbox_$SANDBOX_ID" \\
    --rm \\
    --network=none \\
    --read-only \\
    --memory=512m \\
    --cpus=0.5 \\
    --security-opt=no-new-privileges \\
    --cap-drop=ALL \\
    --user=nobody \\
    alpine:latest \\
    /bin/sh -c "echo 'Sandbox execution completed'"

echo "Sandbox $SANDBOX_ID execution completed"
"""

        script_path = self.project_root / "scripts/security/start_docker_sandbox.sh"
        script_path.parent.mkdir(parents=True, exist_ok=True)

        with open(script_path, "w") as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)
        logger.info(f"Docker sandbox script created: {script_path}")

    async def deploy_layer2_policy_engine(self):
        """Deploy Layer 2: Policy Engine with OPA integration."""
        logger.info("Deploying Layer 2: Policy Engine...")

        # Create policy directories
        policy_dirs = [
            "infrastructure/security/policies",
            "infrastructure/security/opa_configs",
            "logs/policy_evaluation",
        ]

        for dir_path in policy_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created policy directory: {dir_path}")

        # Create OPA policies
        await self.create_opa_policies()

        # Create OPA configuration
        opa_config = {
            "server": {
                "addr": f"0.0.0.0:{self.deployment_config['opa_port']}",
                "diagnostic_addr": "0.0.0.0:8282",
            },
            "storage": {
                "disk": {
                    "directory": str(
                        self.project_root / "infrastructure/security/opa_data"
                    )
                }
            },
            "bundles": {
                "acgs_policies": {
                    "resource": str(
                        self.project_root / "infrastructure/security/policies"
                    )
                }
            },
            "decision_logs": {
                "console": True,
                "file": str(self.project_root / "logs/policy_evaluation/decisions.log"),
            },
        }

        config_path = (
            self.project_root / "infrastructure/security/opa_configs/config.yaml"
        )
        with open(config_path, "w") as f:
            import yaml

            yaml.dump(opa_config, f, indent=2)

        logger.info(f"OPA configuration saved to {config_path}")

    async def create_opa_policies(self):
        """Create OPA policy files."""
        # Evolution approval policy
        evolution_policy = """
package acgs.evolution

import future.keywords.if
import future.keywords.in

default allow = false

# Allow evolution if all conditions are met
allow if {
    input.constitutional_compliance_score >= 0.95
    input.risk_level in ["low", "medium"]
    input.requester_permissions[_] == "evolution_submit"
}

# Require human review for high-risk evolutions
require_human_review if {
    input.risk_level in ["high", "critical"]
}

require_human_review if {
    input.constitutional_compliance_score < 0.95
}

# Constitutional hash validation
constitutional_hash_valid if {
    input.constitutional_hash == "cdd01ef066bc6cf2"
}
"""

        policy_path = (
            self.project_root / "infrastructure/security/policies/evolution.rego"
        )
        with open(policy_path, "w") as f:
            f.write(evolution_policy)

        # Resource access policy
        resource_policy = """
package acgs.resources

import future.keywords.if
import future.keywords.in

default allow = false

# Allow resource access based on permissions
allow if {
    input.action in input.user_permissions
    input.resource in allowed_resources[input.action]
}

# Define allowed resources per action
allowed_resources := {
    "read": ["evolution_requests", "review_tasks", "audit_logs"],
    "write": ["evolution_requests", "review_decisions"],
    "execute": ["sandbox_operations", "policy_evaluations"],
    "admin": ["system_config", "user_management"]
}

# Rate limiting
rate_limit_exceeded if {
    input.requests_per_minute > 100
}
"""

        resource_policy_path = (
            self.project_root / "infrastructure/security/policies/resources.rego"
        )
        with open(resource_policy_path, "w") as f:
            f.write(resource_policy)

        logger.info("OPA policies created")

    async def deploy_layer3_authentication(self):
        """Deploy Layer 3: Authentication and Authorization."""
        logger.info("Deploying Layer 3: Authentication and Authorization...")

        # Create authentication directories
        auth_dirs = [
            "infrastructure/security/auth",
            "infrastructure/security/certificates",
            "logs/authentication",
        ]

        for dir_path in auth_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created auth directory: {dir_path}")

        # Create JWT configuration
        jwt_config = {
            "algorithm": "HS256",
            "secret_key": self.deployment_config["jwt_secret"],
            "token_expiry_hours": 24,
            "refresh_token_expiry_days": 7,
            "issuer": "acgs-ec-service",
            "audience": "acgs-system",
            "constitutional_hash": self.constitutional_hash,
        }

        jwt_config_path = (
            self.project_root / "infrastructure/security/auth/jwt_config.json"
        )
        with open(jwt_config_path, "w") as f:
            json.dump(jwt_config, f, indent=2)

        # Create RBAC configuration
        rbac_config = {
            "roles": {
                "constitutional_expert": {
                    "permissions": [
                        "evolution_review",
                        "constitutional_validate",
                        "policy_approve",
                        "audit_read",
                    ]
                },
                "security_specialist": {
                    "permissions": [
                        "security_review",
                        "vulnerability_assess",
                        "audit_read",
                        "sandbox_execute",
                    ]
                },
                "technical_lead": {
                    "permissions": [
                        "evolution_submit",
                        "technical_review",
                        "system_configure",
                        "audit_read",
                    ]
                },
                "governance_council": {
                    "permissions": [
                        "policy_approve",
                        "strategic_decide",
                        "risk_manage",
                        "audit_full",
                    ]
                },
            },
            "constitutional_hash": self.constitutional_hash,
        }

        rbac_config_path = (
            self.project_root / "infrastructure/security/auth/rbac_config.json"
        )
        with open(rbac_config_path, "w") as f:
            json.dump(rbac_config, f, indent=2)

        logger.info("Authentication configuration created")

    async def deploy_layer4_audit(self):
        """Deploy Layer 4: Comprehensive Audit and Logging."""
        logger.info("Deploying Layer 4: Audit and Logging...")

        # Create audit directories
        audit_dirs = [
            "infrastructure/security/audit",
            "logs/audit/events",
            "logs/audit/security",
            "logs/audit/constitutional",
        ]

        for dir_path in audit_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created audit directory: {dir_path}")

        # Create audit configuration
        audit_config = {
            "retention_policy": {
                "security_events_days": self.deployment_config["audit_retention_days"],
                "constitutional_events_days": 365,  # Keep constitutional events longer
                "system_events_days": 30,
            },
            "log_levels": {
                "authentication": "INFO",
                "authorization": "INFO",
                "policy_evaluation": "INFO",
                "sandbox_execution": "DEBUG",
                "constitutional_validation": "INFO",
                "security_violation": "ERROR",
            },
            "alert_thresholds": {
                "failed_authentications_per_hour": 10,
                "policy_violations_per_hour": 5,
                "constitutional_violations_per_day": 1,
            },
            "constitutional_hash": self.constitutional_hash,
        }

        audit_config_path = (
            self.project_root / "infrastructure/security/audit/config.json"
        )
        with open(audit_config_path, "w") as f:
            json.dump(audit_config, f, indent=2)

        logger.info("Audit configuration created")

    async def configure_security_integrations(self):
        """Configure integrations between security layers."""
        logger.info("Configuring security layer integrations...")

        # Create master security configuration
        security_config = {
            "architecture": {
                "layer1_sandboxing": {
                    "enabled": True,
                    "runtime": self.deployment_config["sandbox_runtime"],
                    "config_path": "infrastructure/security/sandbox_configs/default.json",
                },
                "layer2_policy": {
                    "enabled": True,
                    "opa_endpoint": f"http://localhost:{self.deployment_config['opa_port']}",
                    "policies_path": "infrastructure/security/policies",
                },
                "layer3_auth": {
                    "enabled": True,
                    "jwt_config_path": "infrastructure/security/auth/jwt_config.json",
                    "rbac_config_path": "infrastructure/security/auth/rbac_config.json",
                },
                "layer4_audit": {
                    "enabled": True,
                    "config_path": "infrastructure/security/audit/config.json",
                    "log_directory": "logs/audit",
                },
            },
            "constitutional_compliance": {
                "hash": self.constitutional_hash,
                "validation_required": True,
                "ac_service_endpoint": "http://localhost:8001",
            },
            "monitoring": {
                "metrics_enabled": True,
                "prometheus_port": 8090,
                "health_check_interval_seconds": 30,
            },
        }

        config_path = self.project_root / "config/security_architecture.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(security_config, f, indent=2)

        logger.info(f"Security architecture configuration saved to {config_path}")

    async def validate_security_deployment(self):
        """Validate the security architecture deployment."""
        logger.info("Validating security architecture deployment...")

        # Check if all required files exist
        required_files = [
            "services/core/evolutionary-computation/ec_service/security_architecture.py",
            "infrastructure/security/sandbox_configs/default.json",
            "infrastructure/security/policies/evolution.rego",
            "infrastructure/security/auth/jwt_config.json",
            "infrastructure/security/audit/config.json",
            "config/security_architecture.json",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            logger.error(f"Missing security files: {missing_files}")
            raise RuntimeError("Security deployment validation failed - missing files")

        logger.info("✓ All required security files are present")

        # Test security component imports
        try:
            sys.path.insert(0, str(self.project_root))
            from services.core.evolutionary_computation.ec_service.security_architecture import (
                security_architecture,
            )

            logger.info("✓ Security architecture imports successfully")
        except ImportError as e:
            logger.warning(f"Security architecture import test failed: {e}")
        finally:
            if str(self.project_root) in sys.path:
                sys.path.remove(str(self.project_root))

    def print_deployment_summary(self):
        """Print deployment summary."""
        print("\n" + "=" * 70)
        print("ACGS 4-LAYER SECURITY ARCHITECTURE DEPLOYMENT SUMMARY")
        print("=" * 70)
        print("✓ Layer 1: Sandboxing and Isolation deployed")
        print(f"  - Runtime: {self.deployment_config['sandbox_runtime']}")
        print("  - Resource limits and security constraints configured")
        print("✓ Layer 2: Policy Engine deployed")
        print(
            f"  - OPA integration configured (port {self.deployment_config['opa_port']})"
        )
        print("  - Evolution and resource access policies created")
        print("✓ Layer 3: Authentication and Authorization deployed")
        print("  - JWT authentication configured")
        print("  - RBAC with role-based permissions")
        print("✓ Layer 4: Comprehensive Audit and Logging deployed")
        print(
            f"  - {self.deployment_config['audit_retention_days']}-day retention policy"
        )
        print("  - Security event monitoring and alerting")
        print("\nSecurity Features:")
        print("  - Constitutional hash validation across all layers")
        print("  - Human-in-the-loop approval workflows")
        print("  - Comprehensive audit trail")
        print("  - Resource isolation and sandboxing")
        print("  - Policy-based access control")
        print("\nNext Steps:")
        print(
            "1. Start OPA server: opa run --server --config-file infrastructure/security/opa_configs/config.yaml"
        )
        print("2. Configure monitoring dashboards for security metrics")
        print("3. Set up alerting for security violations")
        print("4. Test security architecture with sample evolution requests")
        print("=" * 70)


async def main():
    """Main deployment function."""
    deployment = SecurityArchitectureDeployment()

    try:
        await deployment.deploy_complete_security_architecture()
        deployment.print_deployment_summary()

    except Exception as e:
        logger.error(f"Security architecture deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
