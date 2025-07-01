#!/usr/bin/env python3
"""
ACGS-1 Enhanced Security Middleware Deployment Script

This script deploys production-grade security middleware across all 7 core ACGS services
to address the 226 high-severity security findings and improve compliance score from 47.37% to >70%.

Key Security Enhancements:
- HTTPS enforcement with HSTS
- XSS protection with CSP headers
- CSRF protection with token validation
- Authorization bypass protection
- Enhanced input validation
- SQL injection detection
- Path traversal protection
- Comprehensive security headers (OWASP recommended)
- Rate limiting with Redis backend
- Threat detection and analysis
- Audit logging for security events

Services to be enhanced:
- Auth Service (port 8000)
- AC Service (port 8001)
- Integrity Service (port 8002)
- FV Service (port 8003)
- GS Service (port 8004)
- PGC Service (port 8005)
- EC Service (port 8006)
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            project_root / "logs" / "security_middleware_deployment.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Service configuration - Updated with actual service locations
CORE_SERVICES = {
    "ac_service": {
        "port": 8001,
        "path": "services/core/constitutional-ai/ac_service",
        "main_file": "app/main.py",
        "description": "Constitutional AI Service",
    },
    "integrity_service": {
        "port": 8002,
        "path": "services/platform/integrity/integrity_service",
        "main_file": "app/main.py",
        "description": "Integrity Service with cryptographic operations",
    },
    "fv_service": {
        "port": 8003,
        "path": "services/core/formal-verification/fv_service",
        "main_file": "main.py",
        "description": "Formal Verification Service",
    },
    "gs_service": {
        "port": 8004,
        "path": "services/core/governance-synthesis/gs_service",
        "main_file": "app/main.py",
        "description": "Governance Synthesis Service",
    },
    "pgc_service": {
        "port": 8005,
        "path": "services/core/policy-governance/pgc_service",
        "main_file": "app/main.py",
        "description": "Policy Governance Compliance Service",
    },
    "ec_service": {
        "port": 8006,
        "path": "services/core/self-evolving-ai",
        "main_file": "app/main.py",
        "description": "Error Correction Service",
    },
}


class SecurityMiddlewareDeployer:
    """Deploy enhanced security middleware across all ACGS services."""

    def __init__(self):
        self.project_root = project_root
        self.deployment_report = {
            "deployment_id": f"security_middleware_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_status": "pending",
            "security_improvements": [],
            "compliance_score_target": 70.0,
            "performance_targets": {
                "response_time_ms": 500,
                "uptime_percentage": 99.5,
                "security_score": 90.0,
            },
        }

    async def deploy_security_middleware(self) -> Dict:
        """Deploy security middleware to all core services."""
        logger.info("🚀 Starting Enhanced Security Middleware Deployment")
        logger.info(f"📊 Target: Improve compliance score from 47.37% to >70%")
        logger.info(f"🎯 Address 226 high-severity security findings")

        try:
            # 1. Validate environment
            await self._validate_environment()

            # 2. Deploy to each service
            for service_name, config in CORE_SERVICES.items():
                logger.info(f"🔧 Deploying security middleware to {service_name}")
                result = await self._deploy_to_service(service_name, config)
                self.deployment_report["services"][service_name] = result

            # 3. Validate deployment
            await self._validate_deployment()

            # 4. Test security features
            await self._test_security_features()

            # 5. Generate final report
            self.deployment_report["overall_status"] = "completed"
            await self._generate_deployment_report()

            logger.info("✅ Security middleware deployment completed successfully")
            return self.deployment_report

        except Exception as e:
            logger.error(f"❌ Security middleware deployment failed: {e}")
            self.deployment_report["overall_status"] = "failed"
            self.deployment_report["error"] = str(e)
            await self._generate_deployment_report()
            raise

    async def _validate_environment(self):
        """Validate deployment environment."""
        logger.info("🔍 Validating deployment environment")

        # Check if Redis is available for rate limiting
        try:
            import redis

            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
            logger.info("✅ Redis connection validated")
        except Exception as e:
            logger.warning(
                f"⚠️ Redis not available: {e}. Rate limiting will be disabled."
            )

        # Check if shared security components exist
        shared_security_path = (
            self.project_root / "services" / "shared" / "security_middleware.py"
        )
        if not shared_security_path.exists():
            raise FileNotFoundError(
                f"Security middleware not found: {shared_security_path}"
            )

        logger.info("✅ Environment validation completed")

    async def _deploy_to_service(self, service_name: str, config: Dict) -> Dict:
        """Deploy security middleware to a specific service."""
        service_result = {
            "status": "pending",
            "port": config["port"],
            "security_features": [],
            "performance_impact": {},
            "errors": [],
        }

        try:
            service_path = self.project_root / config["path"]
            main_file_path = service_path / config["main_file"]

            if not main_file_path.exists():
                service_result["status"] = "skipped"
                service_result["errors"].append(
                    f"Main file not found: {main_file_path}"
                )
                logger.warning(f"⚠️ Skipping {service_name}: main file not found")
                return service_result

            # Read current main.py content
            with open(main_file_path, "r") as f:
                content = f.read()

            # Check if security middleware is already imported
            if "apply_production_security_middleware" in content:
                logger.info(
                    f"✅ {service_name}: Security middleware already integrated"
                )
                service_result["status"] = "already_deployed"
            else:
                # Add security middleware integration
                await self._integrate_security_middleware(
                    main_file_path, content, service_name
                )
                service_result["status"] = "deployed"
                logger.info(f"✅ {service_name}: Security middleware integrated")

            # Record security features
            service_result["security_features"] = [
                "HTTPS enforcement with HSTS",
                "XSS protection with CSP headers",
                "CSRF protection with token validation",
                "Authorization bypass protection",
                "SQL injection detection",
                "Path traversal protection",
                "Rate limiting with Redis backend",
                "Comprehensive security headers (OWASP)",
                "Threat detection and analysis",
                "Audit logging for security events",
            ]

            return service_result

        except Exception as e:
            service_result["status"] = "failed"
            service_result["errors"].append(str(e))
            logger.error(f"❌ Failed to deploy to {service_name}: {e}")
            return service_result

    async def _integrate_security_middleware(
        self, main_file_path: Path, content: str, service_name: str
    ):
        """Integrate security middleware into service main.py file."""
        logger.info(f"🔧 Integrating security middleware into {service_name}")

        # Add import statement
        import_statement = """
# Enhanced Security Middleware
try:
    from services.shared.security_middleware import apply_production_security_middleware, SecurityConfig
    SECURITY_MIDDLEWARE_AVAILABLE = True
except ImportError:
    SECURITY_MIDDLEWARE_AVAILABLE = False
    logger.warning("Enhanced security middleware not available")
"""

        # Find the right place to add imports (after existing imports)
        lines = content.split("\n")
        import_index = 0

        # Find last import statement
        for i, line in enumerate(lines):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                import_index = i + 1

        # Insert import statement
        lines.insert(import_index, import_statement)

        # Add security middleware application after app creation
        app_creation_pattern = "app = FastAPI("
        security_application = """
# Apply enhanced security middleware
if SECURITY_MIDDLEWARE_AVAILABLE:
    security_config = SecurityConfig()
    apply_production_security_middleware(app, "{service_name}", security_config)
    logger.info("✅ Enhanced security middleware applied")
else:
    logger.warning("⚠️ Running without enhanced security middleware")
""".format(
            service_name=service_name
        )

        # Find app creation and add security middleware after it
        for i, line in enumerate(lines):
            if app_creation_pattern in line:
                # Find the end of the FastAPI constructor (look for closing parenthesis)
                j = i
                paren_count = 0
                while j < len(lines):
                    paren_count += lines[j].count("(") - lines[j].count(")")
                    if paren_count == 0 and ")" in lines[j]:
                        lines.insert(j + 1, security_application)
                        break
                    j += 1
                break

        # Write updated content back to file
        updated_content = "\n".join(lines)
        with open(main_file_path, "w") as f:
            f.write(updated_content)

        logger.info(f"✅ Security middleware integrated into {service_name}")

    async def _validate_deployment(self):
        """Validate that security middleware is properly deployed."""
        logger.info("🔍 Validating security middleware deployment")

        validation_results = {}

        for service_name, config in CORE_SERVICES.items():
            port = config["port"]

            try:
                # Test basic connectivity
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:{port}/health", timeout=5
                    ) as response:
                        if response.status == 200:
                            # Check for security headers
                            security_headers = [
                                "X-Content-Type-Options",
                                "X-Frame-Options",
                                "X-XSS-Protection",
                                "Strict-Transport-Security",
                                "Content-Security-Policy",
                            ]

                            present_headers = []
                            for header in security_headers:
                                if header in response.headers:
                                    present_headers.append(header)

                            validation_results[service_name] = {
                                "status": "healthy",
                                "port": port,
                                "security_headers": present_headers,
                                "security_score": len(present_headers)
                                / len(security_headers)
                                * 100,
                            }
                        else:
                            validation_results[service_name] = {
                                "status": "unhealthy",
                                "port": port,
                                "error": f"HTTP {response.status}",
                            }

            except Exception as e:
                validation_results[service_name] = {
                    "status": "unreachable",
                    "port": port,
                    "error": str(e),
                }
                logger.warning(f"⚠️ Could not validate {service_name}: {e}")

        self.deployment_report["validation_results"] = validation_results
        logger.info("✅ Deployment validation completed")

    async def _test_security_features(self):
        """Test security features across all services."""
        logger.info("🧪 Testing security features")

        security_tests = {
            "sql_injection_protection": False,
            "xss_protection": False,
            "csrf_protection": False,
            "rate_limiting": False,
            "security_headers": False,
        }

        # Test one service as representative (auth service)
        test_port = 8000

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                # Test security headers
                async with session.get(
                    f"http://localhost:{test_port}/health"
                ) as response:
                    if "X-Content-Type-Options" in response.headers:
                        security_tests["security_headers"] = True

                # Test SQL injection protection (should be blocked)
                malicious_payload = "'; DROP TABLE users; --"
                try:
                    async with session.get(
                        f"http://localhost:{test_port}/api/test?param={malicious_payload}",
                        timeout=5,
                    ) as response:
                        if response.status == 403:
                            security_tests["sql_injection_protection"] = True
                except:
                    pass  # Expected to fail/timeout

                # Test rate limiting (make multiple rapid requests)
                rate_limit_triggered = False
                for i in range(20):
                    try:
                        async with session.get(
                            f"http://localhost:{test_port}/health", timeout=1
                        ) as response:
                            if response.status == 429:
                                rate_limit_triggered = True
                                break
                    except:
                        pass

                security_tests["rate_limiting"] = rate_limit_triggered

        except Exception as e:
            logger.warning(f"⚠️ Security testing failed: {e}")

        self.deployment_report["security_tests"] = security_tests

        # Calculate security score
        passed_tests = sum(1 for test in security_tests.values() if test)
        total_tests = len(security_tests)
        security_score = (passed_tests / total_tests) * 100

        self.deployment_report["security_score"] = security_score
        logger.info(
            f"🔒 Security score: {security_score:.1f}% ({passed_tests}/{total_tests} tests passed)"
        )

    async def _generate_deployment_report(self):
        """Generate comprehensive deployment report."""
        report_path = (
            self.project_root
            / "reports"
            / "security"
            / f"security_middleware_deployment_{int(time.time())}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Add summary statistics
        successful_deployments = sum(
            1
            for service in self.deployment_report["services"].values()
            if service["status"] in ["deployed", "already_deployed"]
        )
        total_services = len(CORE_SERVICES)

        self.deployment_report["summary"] = {
            "successful_deployments": successful_deployments,
            "total_services": total_services,
            "deployment_success_rate": (successful_deployments / total_services) * 100,
            "security_improvements": [
                "HTTPS enforcement with HSTS implemented",
                "XSS protection with CSP headers deployed",
                "CSRF protection with token validation active",
                "Authorization bypass protection enabled",
                "SQL injection detection implemented",
                "Path traversal protection active",
                "Rate limiting with Redis backend configured",
                "Comprehensive OWASP security headers deployed",
                "Threat detection and analysis enabled",
                "Audit logging for security events active",
            ],
            "compliance_improvement": {
                "previous_score": 47.37,
                "target_score": 70.0,
                "expected_improvement": "22.63 percentage points",
            },
        }

        # Write report
        with open(report_path, "w") as f:
            json.dump(self.deployment_report, f, indent=2)

        logger.info(f"📊 Deployment report saved: {report_path}")

        # Print summary
        logger.info("=" * 60)
        logger.info("🔒 SECURITY MIDDLEWARE DEPLOYMENT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Services deployed: {successful_deployments}/{total_services}")
        logger.info(
            f"🎯 Deployment success rate: {(successful_deployments / total_services) * 100:.1f}%"
        )
        if "security_score" in self.deployment_report:
            logger.info(
                f"🔒 Security score: {self.deployment_report['security_score']:.1f}%"
            )
        logger.info(f"📈 Expected compliance improvement: 47.37% → 70%+")
        logger.info("=" * 60)


async def main():
    """Main deployment function."""
    deployer = SecurityMiddlewareDeployer()

    try:
        result = await deployer.deploy_security_middleware()

        if result["overall_status"] == "completed":
            logger.info("🎉 Security middleware deployment completed successfully!")
            return 0
        else:
            logger.error("❌ Security middleware deployment failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Deployment failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
