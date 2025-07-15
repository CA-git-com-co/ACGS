#!/usr/bin/env python3
"""
Deployment Validation Script
Validates that reorganized services can be deployed and integrated properly
"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path

import aiohttp

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentValidator:
    """Validates deployment readiness after reorganization"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.services_health = {}
        self.blockchain_status = {}

    async def validate_service_health(self) -> bool:
        """Validate that all services are healthy"""
        logger.info("🏥 Validating service health...")

        services = {
            "constitutional-ai": "http://localhost:8001/health",
            "governance-synthesis": "http://localhost:8003/health",
            "policy-governance": "http://localhost:8004/health",
            "formal-verification": "http://localhost:8005/health",
            "authentication": "http://localhost:8002/health",
            "integrity": "http://localhost:8006/health",
        }

        healthy_services = 0
        async with aiohttp.ClientSession() as session:
            for service_name, health_url in services.items():
                try:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            self.services_health[service_name] = "healthy"
                            healthy_services += 1
                            logger.info(f"✅ {service_name}: healthy")
                        else:
                            self.services_health[service_name] = (
                                f"unhealthy ({response.status})"
                            )
                            logger.warning(
                                f"⚠️ {service_name}: unhealthy ({response.status})"
                            )
                except Exception as e:
                    self.services_health[service_name] = f"error ({e!s})"
                    logger.warning(f"❌ {service_name}: error - {e}")

        success_rate = healthy_services / len(services)
        logger.info(
            f"Service health: {healthy_services}/{len(services)} ({success_rate:.1%})"
        )

        return success_rate >= 0.8  # 80% services must be healthy

    async def validate_blockchain_deployment(self) -> bool:
        """Validate Solana program deployment"""
        logger.info("⛓️ Validating blockchain deployment...")

        blockchain_dir = self.root_path / "blockchain"
        if not blockchain_dir.exists():
            logger.error("Blockchain directory not found")
            return False

        # Check if programs are built
        target_dir = blockchain_dir / "target" / "deploy"
        if not target_dir.exists():
            logger.warning("Programs not built, attempting build...")
            try:
                result = subprocess.run(
                    ["anchor", "build"],
                    check=False,
                    cwd=blockchain_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode != 0:
                    logger.error(f"Build failed: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"Build error: {e}")
                return False

        # Check program artifacts
        expected_programs = ["quantumagi_core.so", "appeals.so", "logging.so"]
        missing_programs = []

        for program in expected_programs:
            program_path = target_dir / program
            if program_path.exists():
                self.blockchain_status[program] = "built"
                logger.info(f"✅ {program}: built")
            else:
                self.blockchain_status[program] = "missing"
                missing_programs.append(program)
                logger.warning(f"❌ {program}: missing")

        if missing_programs:
            logger.error(f"Missing programs: {missing_programs}")
            return False

        logger.info("✅ All blockchain programs built successfully")
        return True

    async def validate_integration_endpoints(self) -> bool:
        """Validate integration between services and blockchain"""
        logger.info("🔗 Validating service integrations...")

        integration_tests = [
            self._test_gs_to_blockchain_integration,
            self._test_pgc_compliance_check,
            self._test_constitutional_ai_integration,
        ]

        passed_tests = 0
        for test in integration_tests:
            try:
                if await test():
                    passed_tests += 1
            except Exception as e:
                logger.error(f"Integration test failed: {e}")

        success_rate = passed_tests / len(integration_tests)
        logger.info(
            f"Integration tests: {passed_tests}/{len(integration_tests)} ({success_rate:.1%})"
        )

        return success_rate >= 0.7  # 70% integration tests must pass

    async def _test_gs_to_blockchain_integration(self) -> bool:
        """Test Governance Synthesis to blockchain integration"""
        logger.info("Testing GS → Blockchain integration...")

        # Mock policy synthesis request
        test_policy = {
            "principle_id": "PC-001",
            "content": "No unauthorized state mutations",
            "category": "safety",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Test policy synthesis
                async with session.post(
                    "http://localhost:8003/api/v1/synthesize/",
                    json=test_policy,
                    timeout=10,
                ) as response:
                    if response.status == 200:
                        await response.json()
                        logger.info("✅ GS synthesis endpoint working")
                        return True
                    logger.warning(f"GS synthesis failed: {response.status}")
                    return False
        except Exception as e:
            logger.warning(f"GS integration test failed: {e}")
            return False

    async def _test_pgc_compliance_check(self) -> bool:
        """Test Policy Governance compliance checking"""
        logger.info("Testing PGC compliance checking...")

        test_action = {
            "action_type": "state_mutation",
            "parameters": {"target": "treasury", "amount": 1000},
            "requester": "test_user",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8004/api/v1/enforcement/",
                    json=test_action,
                    timeout=10,
                ) as response:
                    if response.status in [200, 403]:  # 200 = allowed, 403 = denied
                        logger.info("✅ PGC compliance endpoint working")
                        return True
                    logger.warning(f"PGC compliance failed: {response.status}")
                    return False
        except Exception as e:
            logger.warning(f"PGC integration test failed: {e}")
            return False

    async def _test_constitutional_ai_integration(self) -> bool:
        """Test Constitutional AI service integration"""
        logger.info("Testing Constitutional AI integration...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:8001/api/v1/principles/", timeout=10
                ) as response:
                    if response.status == 200:
                        principles = await response.json()
                        logger.info(
                            f"✅ Constitutional AI endpoint working ({len(principles)} principles)"
                        )
                        return True
                    logger.warning(f"Constitutional AI failed: {response.status}")
                    return False
        except Exception as e:
            logger.warning(f"Constitutional AI integration test failed: {e}")
            return False

    def validate_configuration_files(self) -> bool:
        """Validate that all configuration files are properly updated"""
        logger.info("⚙️ Validating configuration files...")

        config_files = [
            "blockchain/Anchor.toml",
            "blockchain/package.json",
            "services/shared/config/service_registry.py",
            "infrastructure/docker/docker-compose.yml",
            "config/environments/developmentconfig/environments/development.env",
        ]

        missing_configs = []
        for config_file in config_files:
            config_path = self.root_path / config_file
            if config_path.exists():
                logger.info(f"✅ {config_file}")
            else:
                missing_configs.append(config_file)
                logger.warning(f"❌ {config_file}: missing")

        if missing_configs:
            logger.error(f"Missing configuration files: {missing_configs}")
            return False

        logger.info("✅ All configuration files present")
        return True

    async def run_full_deployment_validation(self) -> bool:
        """Run complete deployment validation"""
        logger.info("🚀 Starting Deployment Validation")
        logger.info("=" * 50)

        validations = [
            ("Configuration Files", self.validate_configuration_files),
            ("Blockchain Deployment", self.validate_blockchain_deployment),
            ("Service Health", self.validate_service_health),
            ("Integration Endpoints", self.validate_integration_endpoints),
        ]

        all_passed = True
        for name, validation_func in validations:
            logger.info(f"\n📋 {name}")
            logger.info("-" * 30)

            try:
                if asyncio.iscoroutinefunction(validation_func):
                    result = await validation_func()
                else:
                    result = validation_func()

                if not result:
                    all_passed = False
            except Exception as e:
                logger.error(f"Validation {name} failed: {e}")
                all_passed = False

        logger.info("\n" + "=" * 50)
        if all_passed:
            logger.info("🎉 All deployment validations passed!")
        else:
            logger.error("❌ Some deployment validations failed")

        return all_passed

    def generate_validation_report(self) -> dict:
        """Generate detailed validation report"""
        return {
            "timestamp": time.time(),
            "services_health": self.services_health,
            "blockchain_status": self.blockchain_status,
            "validation_summary": {
                "total_services": len(self.services_health),
                "healthy_services": len(
                    [s for s in self.services_health.values() if s == "healthy"]
                ),
                "blockchain_programs": len(self.blockchain_status),
                "built_programs": len(
                    [p for p in self.blockchain_status.values() if p == "built"]
                ),
            },
        }


async def main():
    """Main deployment validation entry point"""
    import sys

    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."

    validator = DeploymentValidator(root_path)
    success = await validator.run_full_deployment_validation()

    # Generate report
    report = validator.generate_validation_report()
    report_path = Path(root_path) / "deployment_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"📊 Validation report saved to: {report_path}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
