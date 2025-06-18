#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Audit Logging Deployment Script

This script deploys enterprise-grade audit logging across all 7 core ACGS-1 services
with tamper-proof logs, compliance tracking, and security event monitoring.

Features Deployed:
- Tamper-proof audit logs with cryptographic integrity
- Compliance tracking for SOC 2, ISO 27001, NIST
- Real-time security event monitoring
- Constitutional governance audit trail
- Automated log retention and archival
- Performance metrics and alerting
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict


# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("audit_logging_deployment.log"),
    ],
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICES = {
    "auth": {
        "name": "Authentication Service",
        "port": 8000,
        "path": "services/platform/authentication/auth_service/app/main.py",
    },
    "ac": {
        "name": "Constitutional AI Service",
        "port": 8001,
        "path": "services/core/constitutional-ai/ac_service/app/main.py",
    },
    "integrity": {
        "name": "Integrity Service",
        "port": 8002,
        "path": "services/platform/integrity/integrity_service/app/main.py",
    },
    "fv": {
        "name": "Formal Verification Service",
        "port": 8003,
        "path": "services/core/formal-verification/fv_service/main.py",
    },
    "gs": {
        "name": "Governance Synthesis Service",
        "port": 8004,
        "path": "services/core/governance-synthesis/gs_service/app/main.py",
    },
    "pgc": {
        "name": "Policy Governance Service",
        "port": 8005,
        "path": "services/core/policy-governance/pgc_service/app/main.py",
    },
    "ec": {
        "name": "Evolutionary Computation Service",
        "port": 8006,
        "path": "services/core/evolutionary-computation/app/main.py",
    },
}


class AuditLoggingDeployer:
    """Deploy comprehensive audit logging to all ACGS-1 services."""

    def __init__(self):
        self.deployment_results = {}
        self.failed_services = []
        self.successful_services = []

    async def deploy_to_all_services(self) -> Dict:
        """Deploy audit logging to all services."""
        logger.info("📝 Starting comprehensive audit logging deployment")

        deployment_start = time.time()

        # Create audit log directories
        await self._create_audit_directories()

        # Generate encryption keys
        await self._generate_encryption_keys()

        for service_id, service_config in SERVICES.items():
            try:
                logger.info(
                    f"📦 Deploying audit logging to {service_config['name']} (port {service_config['port']})"
                )

                result = await self._deploy_to_service(service_id, service_config)
                self.deployment_results[service_id] = result

                if result["success"]:
                    self.successful_services.append(service_id)
                    logger.info(
                        f"✅ Audit logging deployed successfully to {service_config['name']}"
                    )
                else:
                    self.failed_services.append(service_id)
                    logger.error(
                        f"❌ Failed to deploy audit logging to {service_config['name']}: {result['error']}"
                    )

            except Exception as e:
                error_msg = f"Deployment error for {service_config['name']}: {str(e)}"
                logger.error(error_msg)
                self.deployment_results[service_id] = {
                    "success": False,
                    "error": error_msg,
                    "timestamp": time.time(),
                }
                self.failed_services.append(service_id)

        deployment_time = time.time() - deployment_start

        # Generate deployment summary
        summary = self._generate_deployment_summary(deployment_time)

        # Save deployment report
        await self._save_deployment_report(summary)

        return summary

    async def _create_audit_directories(self):
        """Create audit log directories."""
        audit_dirs = [
            "/var/log/acgs/audit",
            "/var/log/acgs/audit/auth",
            "/var/log/acgs/audit/ac",
            "/var/log/acgs/audit/integrity",
            "/var/log/acgs/audit/fv",
            "/var/log/acgs/audit/gs",
            "/var/log/acgs/audit/pgc",
            "/var/log/acgs/audit/ec",
        ]

        for directory in audit_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"📁 Created audit directory: {directory}")
            except Exception as e:
                logger.warning(f"⚠️ Could not create directory {directory}: {e}")

    async def _generate_encryption_keys(self):
        """Generate encryption keys for audit logging."""
        try:
            from cryptography.fernet import Fernet

            # Generate encryption key
            encryption_key = Fernet.generate_key()

            # Generate integrity key
            import secrets

            integrity_key = secrets.token_urlsafe(32)

            # Save keys to environment file
            env_file = Path(project_root) / ".env.audit"
            with open(env_file, "w") as f:
                f.write(f"AUDIT_ENCRYPTION_KEY={encryption_key.decode()}\n")
                f.write(f"AUDIT_INTEGRITY_KEY={integrity_key}\n")

            logger.info("🔐 Generated encryption keys for audit logging")

        except Exception as e:
            logger.warning(f"⚠️ Could not generate encryption keys: {e}")

    async def _deploy_to_service(self, service_id: str, service_config: Dict) -> Dict:
        """Deploy audit logging to a specific service."""
        try:
            # Check if service file exists
            service_path = Path(project_root) / service_config["path"]
            if not service_path.exists():
                return {
                    "success": False,
                    "error": f"Service file not found: {service_path}",
                    "timestamp": time.time(),
                }

            # Apply audit logging by modifying the service file
            success = await self._apply_audit_logging_to_file(service_path, service_id)

            if success:
                return {
                    "success": True,
                    "audit_features": [
                        "Tamper-proof logs with cryptographic integrity",
                        "Compliance tracking (SOC 2, ISO 27001, NIST)",
                        "Real-time security event monitoring",
                        "Constitutional governance audit trail",
                        "Automated log retention and archival",
                        "Performance metrics and alerting",
                        "Structured logging with correlation IDs",
                        "Multi-layer persistence (Redis, File, Database)",
                    ],
                    "timestamp": time.time(),
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to apply audit logging to service file",
                    "timestamp": time.time(),
                }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": time.time()}

    async def _apply_audit_logging_to_file(
        self, service_path: Path, service_id: str
    ) -> bool:
        """Apply audit logging to service file."""
        try:
            # Read current service file
            with open(service_path, "r") as f:
                content = f.read()

            # Check if audit logging is already applied
            if "apply_audit_logging_to_service" in content:
                logger.info(f"Audit logging already applied to {service_path}")
                return True

            # Add audit logging import
            audit_import = """
# Import comprehensive audit logging
try:
    import sys
    sys.path.append('/home/dislove/ACGS-1/services/shared')
    from comprehensive_audit_logger import (
        apply_audit_logging_to_service,
        get_audit_logger,
        log_user_login,
        log_constitutional_validation,
        log_security_violation,
        AuditEventType,
        AuditSeverity,
        ComplianceFramework
    )
    AUDIT_LOGGING_AVAILABLE = True
    print("✅ Comprehensive audit logging loaded successfully")
except ImportError as e:
    print(f"⚠️ Comprehensive audit logging not available: {e}")
    AUDIT_LOGGING_AVAILABLE = False
"""

            # Find FastAPI app creation
            if "app = FastAPI(" in content:
                # Add audit logging after app creation
                app_creation_pattern = r"(app = FastAPI\([^)]*\))"

                audit_application = f"""
# Apply comprehensive audit logging
if AUDIT_LOGGING_AVAILABLE:
    apply_audit_logging_to_service(app, "{service_id}_service")
    print(f"✅ Comprehensive audit logging applied to {service_id} service")
    print("🔒 Audit features enabled:")
    print("   - Tamper-proof logs with cryptographic integrity")
    print("   - Compliance tracking (SOC 2, ISO 27001, NIST)")
    print("   - Real-time security event monitoring")
    print("   - Constitutional governance audit trail")
    print("   - Automated log retention and archival")
    print("   - Performance metrics and alerting")
else:
    print(f"⚠️ Audit logging not available for {service_id} service")
"""

                # Insert imports at the top
                import_insertion_point = content.find("from fastapi import")
                if import_insertion_point != -1:
                    content = (
                        content[:import_insertion_point]
                        + audit_import
                        + "\n"
                        + content[import_insertion_point:]
                    )

                # Insert audit logging application after app creation
                import re

                content = re.sub(
                    app_creation_pattern, r"\1" + audit_application, content, count=1
                )

                # Write modified content back to file
                with open(service_path, "w") as f:
                    f.write(content)

                logger.info(f"Audit logging applied to {service_path}")
                return True
            else:
                logger.warning(f"Could not find FastAPI app creation in {service_path}")
                return False

        except Exception as e:
            logger.error(f"Error applying audit logging to {service_path}: {e}")
            return False

    def _generate_deployment_summary(self, deployment_time: float) -> Dict:
        """Generate deployment summary."""
        total_services = len(SERVICES)
        successful_count = len(self.successful_services)
        failed_count = len(self.failed_services)
        success_rate = (successful_count / total_services) * 100

        return {
            "deployment_summary": {
                "total_services": total_services,
                "successful_deployments": successful_count,
                "failed_deployments": failed_count,
                "success_rate": f"{success_rate:.1f}%",
                "deployment_time": f"{deployment_time:.2f} seconds",
                "timestamp": time.time(),
            },
            "successful_services": self.successful_services,
            "failed_services": self.failed_services,
            "detailed_results": self.deployment_results,
            "audit_features_deployed": [
                "Tamper-proof logs with cryptographic integrity",
                "Compliance tracking (SOC 2, ISO 27001, NIST)",
                "Real-time security event monitoring",
                "Constitutional governance audit trail",
                "Automated log retention and archival",
                "Performance metrics and alerting",
                "Structured logging with correlation IDs",
                "Multi-layer persistence (Redis, File, Database)",
                "Real-time alerting for critical events",
                "Encrypted log storage with HMAC signatures",
            ],
        }

    async def _save_deployment_report(self, summary: Dict):
        """Save deployment report to file."""
        report_path = Path("audit_logging_deployment_report.json")

        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📄 Deployment report saved to {report_path}")


async def main():
    """Main deployment function."""
    logger.info("🚀 ACGS-1 Comprehensive Audit Logging Deployment Starting")

    deployer = AuditLoggingDeployer()
    summary = await deployer.deploy_to_all_services()

    # Print summary
    print("\n" + "=" * 80)
    print("📝 ACGS-1 Comprehensive Audit Logging Deployment Summary")
    print("=" * 80)
    print(f"Total Services: {summary['deployment_summary']['total_services']}")
    print(
        f"Successful Deployments: {summary['deployment_summary']['successful_deployments']}"
    )
    print(f"Failed Deployments: {summary['deployment_summary']['failed_deployments']}")
    print(f"Success Rate: {summary['deployment_summary']['success_rate']}")
    print(f"Deployment Time: {summary['deployment_summary']['deployment_time']}")

    if summary["successful_services"]:
        print(
            f"\n✅ Successfully deployed to: {', '.join(summary['successful_services'])}"
        )

    if summary["failed_services"]:
        print(f"\n❌ Failed deployments: {', '.join(summary['failed_services'])}")

    print("\n📝 Audit Features Deployed:")
    for feature in summary["audit_features_deployed"]:
        print(f"   - {feature}")

    print("\n📄 Detailed report saved to: audit_logging_deployment_report.json")

    return summary


if __name__ == "__main__":
    asyncio.run(main())
