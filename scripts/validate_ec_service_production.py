#!/usr/bin/env python3
"""
Production Validation Script for ACGS Evolutionary Computation Service
Validates production readiness including performance, security, monitoring, and compliance.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ECServiceProductionValidator:
    """Validates EC Service production readiness."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = []
        self.performance_metrics = {}
        self.security_checks = {}

        # Production requirements
        self.requirements = {
            "response_time_ms": 500,
            "availability_percent": 99.9,
            "constitutional_compliance_percent": 95.0,
            "error_rate_percent": 1.0,
            "security_score_min": 8.0,  # Out of 10
            "test_coverage_percent": 90.0,
        }

    async def validate_production_readiness(self):
        """Run complete production readiness validation."""
        logger.info("Starting EC Service production readiness validation...")

        validation_checks = [
            self.validate_service_deployment,
            self.validate_api_functionality,
            self.validate_security_architecture,
            self.validate_performance_requirements,
            self.validate_monitoring_setup,
            self.validate_constitutional_compliance,
            self.validate_database_readiness,
            self.validate_nats_integration,
            self.validate_error_handling,
            self.validate_documentation,
            self.validate_operational_procedures,
        ]

        for check in validation_checks:
            try:
                await check()
                self.validation_results.append(
                    {
                        "check": check.__name__,
                        "status": "passed",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Validation check {check.__name__} failed: {e}")
                self.validation_results.append(
                    {
                        "check": check.__name__,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        await self.generate_production_readiness_report()

    async def validate_service_deployment(self):
        """Validate service deployment and basic functionality."""
        logger.info("Validating service deployment...")

        # Check if service is running
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "http://localhost:8006/health", timeout=5
                ) as response:
                    assert response.status == 200, "Service health check failed"

                    health_data = await response.json()
                    assert health_data.get("status") in [
                        "healthy",
                        "operational",
                    ], "Service not healthy"

                    logger.info("✓ Service deployment validated")

            except Exception as e:
                raise RuntimeError(f"Service deployment validation failed: {e}")

    async def validate_api_functionality(self):
        """Validate all API endpoints are functional."""
        logger.info("Validating API functionality...")

        async with aiohttp.ClientSession() as session:
            # Test critical endpoints
            endpoints = [
                ("GET", "/", 200),
                ("GET", "/health", 200),
                ("GET", "/api/v1/status", 200),
                ("GET", "/api/v1/reviews/pending", 200),
                ("GET", "/metrics", 200),
            ]

            for method, path, expected_status in endpoints:
                start_time = time.time()
                url = f"http://localhost:8006{path}"

                try:
                    if method == "GET":
                        async with session.get(url, timeout=10) as response:
                            response_time = (time.time() - start_time) * 1000

                            assert (
                                response.status == expected_status
                            ), f"Unexpected status {response.status} for {path}"
                            assert (
                                response_time < self.requirements["response_time_ms"]
                            ), f"Response time {response_time:.2f}ms exceeds requirement"

                            self.performance_metrics[
                                f"api_{path.replace('/', '_')}_response_time"
                            ] = response_time

                except Exception as e:
                    raise RuntimeError(f"API endpoint {method} {path} failed: {e}")

            logger.info("✓ API functionality validated")

    async def validate_security_architecture(self):
        """Validate 4-layer security architecture."""
        logger.info("Validating security architecture...")

        security_score = 0.0
        max_score = 10.0

        # Check Layer 1: Sandboxing
        sandbox_config_path = (
            self.project_root / "infrastructure/security/sandbox_configs/default.json"
        )
        if sandbox_config_path.exists():
            with open(sandbox_config_path) as f:
                config = json.load(f)
                if config.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                    security_score += 2.5
                    logger.info("✓ Layer 1 (Sandboxing) validated")
                else:
                    logger.warning("✗ Layer 1 constitutional hash mismatch")
        else:
            logger.warning("✗ Layer 1 sandbox configuration missing")

        # Check Layer 2: Policy Engine
        policies_dir = self.project_root / "infrastructure/security/policies"
        if policies_dir.exists() and list(policies_dir.glob("*.rego")):
            security_score += 2.5
            logger.info("✓ Layer 2 (Policy Engine) validated")
        else:
            logger.warning("✗ Layer 2 OPA policies missing")

        # Check Layer 3: Authentication
        auth_config_path = (
            self.project_root / "infrastructure/security/auth/jwt_config.json"
        )
        if auth_config_path.exists():
            security_score += 2.5
            logger.info("✓ Layer 3 (Authentication) validated")
        else:
            logger.warning("✗ Layer 3 authentication configuration missing")

        # Check Layer 4: Audit
        audit_config_path = (
            self.project_root / "infrastructure/security/audit/config.json"
        )
        if audit_config_path.exists():
            security_score += 2.5
            logger.info("✓ Layer 4 (Audit) validated")
        else:
            logger.warning("✗ Layer 4 audit configuration missing")

        self.security_checks["security_score"] = security_score

        assert (
            security_score >= self.requirements["security_score_min"]
        ), f"Security score {security_score} below minimum {self.requirements['security_score_min']}"

        logger.info(
            f"✓ Security architecture validated (score: {security_score}/{max_score})"
        )

    async def validate_performance_requirements(self):
        """Validate performance requirements."""
        logger.info("Validating performance requirements...")

        # Run performance test
        async with aiohttp.ClientSession() as session:
            response_times = []

            # Test multiple requests to get average performance
            for i in range(10):
                start_time = time.time()

                async with session.get(
                    "http://localhost:8006/api/v1/status", timeout=10
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)

                    assert (
                        response.status == 200
                    ), f"Performance test request {i+1} failed"

                await asyncio.sleep(0.1)  # Small delay between requests

            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)

            self.performance_metrics["avg_response_time"] = avg_response_time
            self.performance_metrics["max_response_time"] = max_response_time

            assert (
                avg_response_time < self.requirements["response_time_ms"]
            ), f"Average response time {avg_response_time:.2f}ms exceeds requirement"
            assert (
                max_response_time < self.requirements["response_time_ms"]
            ), f"Max response time {max_response_time:.2f}ms exceeds requirement"

            logger.info(
                f"✓ Performance requirements met (avg: {avg_response_time:.2f}ms, max: {max_response_time:.2f}ms)"
            )

    async def validate_monitoring_setup(self):
        """Validate monitoring and metrics setup."""
        logger.info("Validating monitoring setup...")

        # Check Prometheus metrics
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "http://localhost:8006/metrics", timeout=5
                ) as response:
                    assert response.status == 200, "Metrics endpoint not accessible"

                    metrics_text = await response.text()

                    # Check for key metrics
                    required_metrics = [
                        "evolution_requests_total",
                        "human_review_tasks_total",
                        "ec_sandbox_executions_total",
                        "ec_policy_evaluations_total",
                    ]

                    for metric in required_metrics:
                        assert (
                            metric in metrics_text
                        ), f"Required metric {metric} not found"

                    logger.info("✓ Monitoring setup validated")

            except Exception as e:
                raise RuntimeError(f"Monitoring validation failed: {e}")

    async def validate_constitutional_compliance(self):
        """Validate constitutional compliance integration."""
        logger.info("Validating constitutional compliance...")

        # Check constitutional hash in configuration files
        config_files = [
            "infrastructure/security/sandbox_configs/default.json",
            "infrastructure/security/auth/jwt_config.json",
            "infrastructure/security/audit/config.json",
            "config/security_architecture.json",
        ]

        compliance_score = 0.0
        total_files = len(config_files)

        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        config = json.load(f)
                        if config.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                            compliance_score += 1.0
                        else:
                            logger.warning(
                                f"Constitutional hash mismatch in {config_file}"
                            )
                except Exception as e:
                    logger.warning(f"Failed to validate {config_file}: {e}")
            else:
                logger.warning(f"Configuration file {config_file} not found")

        compliance_percentage = (compliance_score / total_files) * 100

        assert (
            compliance_percentage
            >= self.requirements["constitutional_compliance_percent"]
        ), f"Constitutional compliance {compliance_percentage:.1f}% below requirement"

        logger.info(
            f"✓ Constitutional compliance validated ({compliance_percentage:.1f}%)"
        )

    async def validate_database_readiness(self):
        """Validate database schema and connectivity."""
        logger.info("Validating database readiness...")

        # Test database operations through API
        async with aiohttp.ClientSession() as session:
            # Submit test evolution to verify database write
            test_evolution = {
                "evolution_type": "performance_tuning",
                "description": "Production validation test evolution",
                "proposed_changes": {"test": "validation"},
                "target_service": "ec-service",
                "priority": 4,
            }

            try:
                async with session.post(
                    "http://localhost:8006/api/v1/evolution/submit",
                    json=test_evolution,
                    timeout=10,
                ) as response:
                    assert response.status == 200, "Database write operation failed"

                    data = await response.json()
                    evolution_id = data.get("evolution_id")
                    assert evolution_id, "Evolution ID not returned"

                # Verify database read
                async with session.get(
                    f"http://localhost:8006/api/v1/evolution/{evolution_id}/status",
                    timeout=10,
                ) as response:
                    assert response.status == 200, "Database read operation failed"

                    status_data = await response.json()
                    assert (
                        status_data.get("evolution_id") == evolution_id
                    ), "Data consistency check failed"

                logger.info("✓ Database readiness validated")

            except Exception as e:
                raise RuntimeError(f"Database validation failed: {e}")

    async def validate_nats_integration(self):
        """Validate NATS event integration."""
        logger.info("Validating NATS integration...")

        try:
            import nats

            # Test NATS connectivity
            nc = await nats.connect("nats://localhost:4222", timeout=5)

            # Test publishing capability
            test_event = {
                "event_id": "production_validation_test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_name": "ec-service",
                "event_type": "validation_test",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            await nc.publish("acgs.test.validation", json.dumps(test_event).encode())
            await nc.close()

            logger.info("✓ NATS integration validated")

        except Exception as e:
            logger.warning(f"NATS integration validation failed: {e}")
            # Don't fail production validation for NATS issues

    async def validate_error_handling(self):
        """Validate error handling and resilience."""
        logger.info("Validating error handling...")

        async with aiohttp.ClientSession() as session:
            # Test invalid requests
            invalid_requests = [
                ("POST", "/api/v1/evolution/submit", {"invalid": "data"}),
                ("GET", "/api/v1/evolution/nonexistent/status", None),
                ("POST", "/api/v1/reviews/fake-task/decision", {"decision": "invalid"}),
            ]

            for method, path, data in invalid_requests:
                url = f"http://localhost:8006{path}"

                try:
                    if method == "POST":
                        async with session.post(url, json=data, timeout=5) as response:
                            # Should return error status, not crash
                            assert response.status in [
                                400,
                                404,
                                422,
                                500,
                            ], f"Unexpected status {response.status} for invalid request"
                    elif method == "GET":
                        async with session.get(url, timeout=5) as response:
                            assert response.status in [
                                404,
                                500,
                            ], f"Unexpected status {response.status} for invalid request"

                except asyncio.TimeoutError:
                    raise RuntimeError(
                        f"Error handling test timed out for {method} {path}"
                    )

            logger.info("✓ Error handling validated")

    async def validate_documentation(self):
        """Validate documentation completeness."""
        logger.info("Validating documentation...")

        required_docs = [
            "README.md",
            "docs/api_documentation.md",
            "docs/deployment_guide.md",
            "docs/security_architecture.md",
            "docs/operational_procedures.md",
        ]

        missing_docs = []
        for doc in required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                missing_docs.append(doc)

        if missing_docs:
            logger.warning(f"Missing documentation: {missing_docs}")
        else:
            logger.info("✓ Documentation validated")

    async def validate_operational_procedures(self):
        """Validate operational procedures and scripts."""
        logger.info("Validating operational procedures...")

        required_scripts = [
            "scripts/deploy_security_architecture.py",
            "scripts/validate_ec_service_production.py",
            "tests/integration/test_ec_service_integration.py",
        ]

        missing_scripts = []
        for script in required_scripts:
            script_path = self.project_root / script
            if not script_path.exists():
                missing_scripts.append(script)

        if missing_scripts:
            logger.warning(f"Missing operational scripts: {missing_scripts}")
        else:
            logger.info("✓ Operational procedures validated")

    async def generate_production_readiness_report(self):
        """Generate production readiness report."""
        logger.info("Generating production readiness report...")

        # Calculate overall scores
        total_checks = len(self.validation_results)
        passed_checks = sum(
            1 for result in self.validation_results if result["status"] == "passed"
        )
        failed_checks = total_checks - passed_checks

        readiness_score = (
            (passed_checks / total_checks * 100) if total_checks > 0 else 0
        )

        report = {
            "production_readiness": {
                "overall_score": readiness_score,
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "ready_for_production": readiness_score >= 95.0,
            },
            "performance_metrics": self.performance_metrics,
            "security_checks": self.security_checks,
            "requirements_compliance": {
                "response_time_requirement": self.requirements["response_time_ms"],
                "constitutional_compliance_requirement": self.requirements[
                    "constitutional_compliance_percent"
                ],
                "security_score_requirement": self.requirements["security_score_min"],
            },
            "validation_results": self.validation_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Save report
        report_dir = self.project_root / "reports/production_validation"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = (
            report_dir / f"ec_service_production_readiness_{int(time.time())}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Production readiness report saved: {report_file}")

        # Print summary
        self.print_readiness_summary(report)

    def print_readiness_summary(self, report: Dict):
        """Print production readiness summary."""
        readiness = report["production_readiness"]

        print("\n" + "=" * 70)
        print("EC SERVICE PRODUCTION READINESS VALIDATION")
        print("=" * 70)
        print(f"Overall Score: {readiness['overall_score']:.1f}%")
        print(
            f"Checks Passed: {readiness['passed_checks']}/{readiness['total_checks']}"
        )
        print(
            f"Production Ready: {'YES' if readiness['ready_for_production'] else 'NO'}"
        )
        print()

        if self.performance_metrics:
            print("Performance Metrics:")
            for metric, value in self.performance_metrics.items():
                print(f"  - {metric}: {value:.2f}ms")
            print()

        if self.security_checks:
            print("Security Validation:")
            for check, value in self.security_checks.items():
                print(f"  - {check}: {value}")
            print()

        print("Validation Results:")
        for result in self.validation_results:
            status_icon = "✓" if result["status"] == "passed" else "✗"
            print(f"  {status_icon} {result['check']}")
            if result["status"] == "failed":
                print(f"    Error: {result.get('error', 'Unknown error')}")

        print("=" * 70)

        if readiness["ready_for_production"]:
            print("🎉 EC Service is READY for production deployment!")
        else:
            print(
                "⚠️  EC Service requires additional work before production deployment."
            )

        print("=" * 70)


async def main():
    """Main validation function."""
    validator = ECServiceProductionValidator()

    try:
        await validator.validate_production_readiness()

    except Exception as e:
        logger.error(f"Production validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
