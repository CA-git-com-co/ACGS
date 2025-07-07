#!/usr/bin/env python3
"""
ACGS Unified Test Orchestrator
Constitutional Hash: cdd01ef066bc6cf2

Consolidates and modernizes all testing infrastructure for ACGS.

Features:
- Unified test runner for all test types
- Async/await test execution with parallelization
- Comprehensive coverage analysis (>80% target)
- Integration tests with ACGS services
- Performance benchmarking
- Constitutional compliance validation
- Real-time test reporting and monitoring
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import pytest
from pydantic import BaseModel

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS service configuration
ACGS_SERVICES = {
    "auth": {"port": 8016, "name": "Auth Service"},
    "constitutional_ai": {"port": 8001, "name": "Constitutional AI"},
    "integrity": {"port": 8002, "name": "Integrity Service"},
    "formal_verification": {"port": 8003, "name": "Formal Verification"},
    "governance_synthesis": {"port": 8004, "name": "Governance Synthesis"},
    "policy_governance": {"port": 8005, "name": "Policy Governance"},
    "evolutionary_computation": {"port": 8006, "name": "Evolutionary Computation"},
}

# Test configuration
TEST_CONFIG = {
    "coverage_target": 80.0,
    "performance_targets": {
        "p99_latency_ms": 5.0,
        "min_throughput_rps": 100.0,
        "min_cache_hit_rate": 0.85,
    },
    "timeout_seconds": 300,
    "parallel_workers": 4,
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure."""
    test_suite: str
    test_name: str
    status: str  # "passed", "failed", "skipped", "error"
    duration_seconds: float
    error_message: Optional[str] = None
    coverage_percentage: Optional[float] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class TestSuiteResult:
    """Test suite result aggregation."""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_duration_seconds: float
    coverage_percentage: float
    constitutional_compliance: bool
    test_results: List[TestResult]


class TestSuiteConfig(BaseModel):
    """Configuration for test suites."""
    name: str
    test_paths: List[str]
    pytest_args: List[str]
    coverage_paths: List[str]
    parallel: bool = True
    timeout: int = 300
    required_services: List[str] = []


class ACGSTestOrchestrator:
    """Unified test orchestrator for ACGS."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: List[TestSuiteResult] = []
        self.start_time = time.time()
        
        # Define test suites
        self.test_suites = {
            "unit": TestSuiteConfig(
                name="Unit Tests",
                test_paths=["tests/unit/", "tests/core/"],
                pytest_args=["-v", "--tb=short", "--disable-warnings"],
                coverage_paths=["services/", "scripts/", "tools/"],
                parallel=True,
                timeout=120,
            ),
            "integration": TestSuiteConfig(
                name="Integration Tests",
                test_paths=["tests/integration/", "tests/e2e/"],
                pytest_args=["-v", "--tb=short", "--disable-warnings", "-s"],
                coverage_paths=["services/", "scripts/"],
                parallel=False,  # Integration tests may conflict
                timeout=300,
                required_services=["auth", "postgresql", "redis"],
            ),
            "performance": TestSuiteConfig(
                name="Performance Tests",
                test_paths=["tests/performance/", "tests/load/"],
                pytest_args=["-v", "--tb=short", "--disable-warnings", "-s"],
                coverage_paths=["services/"],
                parallel=False,  # Performance tests need isolation
                timeout=600,
                required_services=["auth", "constitutional_ai"],
            ),
            "security": TestSuiteConfig(
                name="Security Tests",
                test_paths=["tests/security/"],
                pytest_args=["-v", "--tb=short", "--disable-warnings"],
                coverage_paths=["services/", "scripts/"],
                parallel=True,
                timeout=180,
            ),
            "constitutional": TestSuiteConfig(
                name="Constitutional Compliance Tests",
                test_paths=["tests/constitutional/", "tests/compliance/"],
                pytest_args=["-v", "--tb=short", "--disable-warnings"],
                coverage_paths=["services/", "tools/"],
                parallel=True,
                timeout=120,
            ),
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize test orchestrator."""
        logger.info("🚀 Initializing ACGS Test Orchestrator...")
        
        # Initialize HTTP session for service checks
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Validate constitutional hash
        if not self._validate_constitutional_hash():
            raise ValueError(f"Invalid constitutional hash: {CONSTITUTIONAL_HASH}")
        
        # Create test directories
        self._create_test_directories()
        
        logger.info("✅ Test orchestrator initialized")
        
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("🧹 Cleaning up test orchestrator...")
        
        if self.session:
            await self.session.close()
            
        logger.info("✅ Cleanup completed")

    def _validate_constitutional_hash(self) -> bool:
        """Validate constitutional hash."""
        return CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

    def _create_test_directories(self):
        """Create necessary test directories."""
        test_dirs = [
            "tests/unit",
            "tests/integration", 
            "tests/e2e",
            "tests/performance",
            "tests/load",
            "tests/security",
            "tests/constitutional",
            "tests/compliance",
            "reports/test_results",
            "reports/coverage",
        ]
        
        for test_dir in test_dirs:
            Path(test_dir).mkdir(parents=True, exist_ok=True)

    async def run_all_tests(self, suites: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run all test suites or specified suites."""
        logger.info("🧪 Starting comprehensive test execution...")
        
        # Determine which suites to run
        suites_to_run = suites or list(self.test_suites.keys())
        
        results = {
            "execution_start": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "suites_executed": suites_to_run,
            "service_health": {},
            "suite_results": {},
            "overall_summary": {},
            "coverage_report": {},
            "recommendations": [],
        }
        
        try:
            # Check service health first
            results["service_health"] = await self._check_service_health()
            
            # Run test suites
            suite_tasks = []
            for suite_name in suites_to_run:
                if suite_name in self.test_suites:
                    suite_config = self.test_suites[suite_name]
                    task = self._run_test_suite(suite_name, suite_config)
                    suite_tasks.append(task)
            
            # Execute test suites (some in parallel, some sequential)
            suite_results = await self._execute_test_suites(suite_tasks, suites_to_run)
            results["suite_results"] = suite_results
            
            # Generate overall summary
            results["overall_summary"] = self._generate_overall_summary(suite_results)
            
            # Generate coverage report
            results["coverage_report"] = await self._generate_coverage_report()
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)
            
            # Save results
            await self._save_test_results(results)
            
            logger.info("✅ Comprehensive test execution completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            results["error"] = str(e)
            return results

    async def _check_service_health(self) -> Dict[str, Any]:
        """Check health of ACGS services."""
        logger.info("🏥 Checking ACGS service health...")
        
        async def check_service(service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
            """Check individual service health."""
            try:
                url = f"http://localhost:{config['port']}/health"
                async with self.session.get(url) as response:
                    return {
                        "service": service_name,
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "status_code": response.status,
                        "available": response.status == 200,
                    }
            except Exception as e:
                return {
                    "service": service_name,
                    "status": "error",
                    "error": str(e),
                    "available": False,
                }
        
        # Check all services concurrently
        tasks = [
            check_service(name, config) 
            for name, config in ACGS_SERVICES.items()
        ]
        
        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        healthy_services = sum(1 for r in health_results if r.get("available", False))
        total_services = len(ACGS_SERVICES)
        
        return {
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": (healthy_services / total_services) * 100,
            "services": health_results,
            "all_healthy": healthy_services == total_services,
        }

    async def _execute_test_suites(
        self, 
        suite_tasks: List, 
        suite_names: List[str]
    ) -> Dict[str, TestSuiteResult]:
        """Execute test suites with proper sequencing."""
        results = {}
        
        # Separate parallel and sequential suites
        parallel_suites = []
        sequential_suites = []
        
        for i, suite_name in enumerate(suite_names):
            suite_config = self.test_suites.get(suite_name)
            if suite_config and suite_config.parallel:
                parallel_suites.append((suite_name, suite_tasks[i]))
            else:
                sequential_suites.append((suite_name, suite_tasks[i]))
        
        # Run parallel suites first
        if parallel_suites:
            logger.info(f"🔄 Running {len(parallel_suites)} parallel test suites...")
            parallel_tasks = [task for _, task in parallel_suites]
            parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
            
            for i, (suite_name, _) in enumerate(parallel_suites):
                if isinstance(parallel_results[i], Exception):
                    logger.error(f"❌ Parallel suite {suite_name} failed: {parallel_results[i]}")
                    results[suite_name] = self._create_error_result(suite_name, str(parallel_results[i]))
                else:
                    results[suite_name] = parallel_results[i]
        
        # Run sequential suites
        for suite_name, task in sequential_suites:
            logger.info(f"🔄 Running sequential test suite: {suite_name}")
            try:
                result = await task
                results[suite_name] = result
            except Exception as e:
                logger.error(f"❌ Sequential suite {suite_name} failed: {e}")
                results[suite_name] = self._create_error_result(suite_name, str(e))
        
        return results

    async def _run_test_suite(self, suite_name: str, config: TestSuiteConfig) -> TestSuiteResult:
        """Run a single test suite."""
        logger.info(f"🧪 Running test suite: {config.name}")
        start_time = time.time()
        
        try:
            # Check required services
            if config.required_services:
                service_check = await self._check_required_services(config.required_services)
                if not service_check["all_available"]:
                    missing = service_check["missing_services"]
                    raise RuntimeError(f"Required services not available: {missing}")
            
            # Build pytest command
            cmd = self._build_pytest_command(config)
            
            # Execute tests
            result = await self._execute_pytest_command(cmd, config.timeout)
            
            # Parse results
            suite_result = self._parse_test_results(suite_name, config, result, start_time)
            
            logger.info(
                f"✅ Test suite {config.name} completed: "
                f"{suite_result.passed_tests}/{suite_result.total_tests} passed"
            )
            
            return suite_result
            
        except Exception as e:
            logger.error(f"❌ Test suite {config.name} failed: {e}")
            return self._create_error_result(suite_name, str(e), start_time)

    async def _check_required_services(self, required_services: List[str]) -> Dict[str, Any]:
        """Check if required services are available."""
        available_services = []
        missing_services = []
        
        for service_name in required_services:
            if service_name in ACGS_SERVICES:
                config = ACGS_SERVICES[service_name]
                try:
                    url = f"http://localhost:{config['port']}/health"
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            available_services.append(service_name)
                        else:
                            missing_services.append(service_name)
                except Exception:
                    missing_services.append(service_name)
            else:
                missing_services.append(service_name)
        
        return {
            "available_services": available_services,
            "missing_services": missing_services,
            "all_available": len(missing_services) == 0,
        }

    def _build_pytest_command(self, config: TestSuiteConfig) -> List[str]:
        """Build pytest command for test suite."""
        cmd = ["python", "-m", "pytest"]

        # Add test paths
        for path in config.test_paths:
            if Path(path).exists():
                cmd.append(path)

        # Add pytest arguments
        cmd.extend(config.pytest_args)

        # Add coverage if specified
        if config.coverage_paths:
            for path in config.coverage_paths:
                cmd.extend(["--cov", path])

            # Coverage reporting
            cmd.extend([
                "--cov-report=term-missing",
                "--cov-report=json:reports/coverage/coverage.json",
                "--cov-report=html:reports/coverage/html",
                f"--cov-fail-under={TEST_CONFIG['coverage_target']}",
            ])

        # Add constitutional hash as environment variable
        cmd.extend(["--tb=short", "-v"])

        return cmd

    async def _execute_pytest_command(self, cmd: List[str], timeout: int) -> Dict[str, Any]:
        """Execute pytest command asynchronously."""
        logger.info(f"🔧 Executing: {' '.join(cmd)}")

        try:
            # Set environment variables
            env = {
                "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
                "ENVIRONMENT": "testing",
                "PYTHONPATH": str(Path.cwd()),
            }

            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(Path.cwd())
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(f"Test execution timed out after {timeout}s")

            return {
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore"),
                "success": process.returncode == 0,
            }

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "error": str(e),
            }

    def _parse_test_results(
        self,
        suite_name: str,
        config: TestSuiteConfig,
        result: Dict[str, Any],
        start_time: float
    ) -> TestSuiteResult:
        """Parse pytest results into structured format."""
        duration = time.time() - start_time

        # Parse stdout for test results
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")

        # Extract test counts from pytest output
        passed_tests = stdout.count(" PASSED")
        failed_tests = stdout.count(" FAILED")
        skipped_tests = stdout.count(" SKIPPED")
        error_tests = stdout.count(" ERROR")
        total_tests = passed_tests + failed_tests + skipped_tests + error_tests

        # Extract coverage percentage
        coverage_percentage = self._extract_coverage_percentage(stdout)

        # Check constitutional compliance
        constitutional_compliance = CONSTITUTIONAL_HASH in stdout or result.get("success", False)

        # Create individual test results (simplified)
        test_results = []
        if total_tests > 0:
            # Create summary test results
            if passed_tests > 0:
                test_results.append(TestResult(
                    test_suite=suite_name,
                    test_name=f"{config.name} - Passed Tests",
                    status="passed",
                    duration_seconds=duration / total_tests,
                    coverage_percentage=coverage_percentage,
                ))

            if failed_tests > 0:
                test_results.append(TestResult(
                    test_suite=suite_name,
                    test_name=f"{config.name} - Failed Tests",
                    status="failed",
                    duration_seconds=duration / total_tests,
                    error_message=stderr[:500] if stderr else "Test failures detected",
                ))

        return TestSuiteResult(
            suite_name=config.name,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            total_duration_seconds=duration,
            coverage_percentage=coverage_percentage,
            constitutional_compliance=constitutional_compliance,
            test_results=test_results,
        )

    def _extract_coverage_percentage(self, output: str) -> float:
        """Extract coverage percentage from pytest output."""
        try:
            # Look for coverage percentage in output
            lines = output.split('\n')
            for line in lines:
                if "TOTAL" in line and "%" in line:
                    # Extract percentage from line like "TOTAL    100    25    75%"
                    parts = line.split()
                    for part in parts:
                        if part.endswith('%'):
                            return float(part[:-1])
            return 0.0
        except Exception:
            return 0.0

    def _create_error_result(
        self,
        suite_name: str,
        error_message: str,
        start_time: Optional[float] = None
    ) -> TestSuiteResult:
        """Create error result for failed test suite."""
        duration = time.time() - start_time if start_time else 0.0

        error_test = TestResult(
            test_suite=suite_name,
            test_name=f"{suite_name} - Execution Error",
            status="error",
            duration_seconds=duration,
            error_message=error_message,
        )

        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=1,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            error_tests=1,
            total_duration_seconds=duration,
            coverage_percentage=0.0,
            constitutional_compliance=False,
            test_results=[error_test],
        )

    def _generate_overall_summary(self, suite_results: Dict[str, TestSuiteResult]) -> Dict[str, Any]:
        """Generate overall test execution summary."""
        total_tests = sum(result.total_tests for result in suite_results.values())
        total_passed = sum(result.passed_tests for result in suite_results.values())
        total_failed = sum(result.failed_tests for result in suite_results.values())
        total_skipped = sum(result.skipped_tests for result in suite_results.values())
        total_errors = sum(result.error_tests for result in suite_results.values())
        total_duration = sum(result.total_duration_seconds for result in suite_results.values())

        # Calculate weighted average coverage
        coverage_values = [r.coverage_percentage for r in suite_results.values() if r.coverage_percentage > 0]
        avg_coverage = sum(coverage_values) / len(coverage_values) if coverage_values else 0.0

        # Check constitutional compliance
        all_compliant = all(result.constitutional_compliance for result in suite_results.values())

        # Calculate success rate
        success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0.0

        return {
            "total_tests": total_tests,
            "passed_tests": total_passed,
            "failed_tests": total_failed,
            "skipped_tests": total_skipped,
            "error_tests": total_errors,
            "success_rate_percentage": round(success_rate, 2),
            "total_duration_seconds": round(total_duration, 2),
            "average_coverage_percentage": round(avg_coverage, 2),
            "constitutional_compliance": all_compliant,
            "meets_coverage_target": avg_coverage >= TEST_CONFIG["coverage_target"],
            "overall_status": "PASSED" if total_failed == 0 and total_errors == 0 else "FAILED",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    async def _generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report."""
        logger.info("📊 Generating coverage report...")

        try:
            # Check if coverage.json exists
            coverage_file = Path("reports/coverage/coverage.json")
            if coverage_file.exists():
                with open(coverage_file, "r") as f:
                    coverage_data = json.load(f)

                # Extract key metrics
                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0.0)

                # Get file-level coverage
                files_coverage = {}
                for filename, file_data in coverage_data.get("files", {}).items():
                    files_coverage[filename] = {
                        "coverage_percentage": file_data.get("summary", {}).get("percent_covered", 0.0),
                        "missing_lines": file_data.get("missing_lines", []),
                        "executed_lines": file_data.get("executed_lines", []),
                    }

                return {
                    "total_coverage_percentage": round(total_coverage, 2),
                    "meets_target": total_coverage >= TEST_CONFIG["coverage_target"],
                    "target_percentage": TEST_CONFIG["coverage_target"],
                    "files_coverage": files_coverage,
                    "report_generated": True,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }
            else:
                return {
                    "total_coverage_percentage": 0.0,
                    "meets_target": False,
                    "target_percentage": TEST_CONFIG["coverage_target"],
                    "report_generated": False,
                    "error": "Coverage report not found",
                }

        except Exception as e:
            logger.error(f"Coverage report generation failed: {e}")
            return {
                "total_coverage_percentage": 0.0,
                "meets_target": False,
                "error": str(e),
            }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        overall_summary = results.get("overall_summary", {})
        coverage_report = results.get("coverage_report", {})
        service_health = results.get("service_health", {})

        # Coverage recommendations
        coverage_percentage = coverage_report.get("total_coverage_percentage", 0.0)
        if coverage_percentage < TEST_CONFIG["coverage_target"]:
            recommendations.append(
                f"Improve test coverage from {coverage_percentage:.1f}% to >{TEST_CONFIG['coverage_target']}%"
            )

        # Test failure recommendations
        failed_tests = overall_summary.get("failed_tests", 0)
        error_tests = overall_summary.get("error_tests", 0)
        if failed_tests > 0:
            recommendations.append(f"Fix {failed_tests} failing tests")
        if error_tests > 0:
            recommendations.append(f"Resolve {error_tests} test execution errors")

        # Service health recommendations
        if not service_health.get("all_healthy", False):
            unhealthy_count = service_health.get("total_services", 0) - service_health.get("healthy_services", 0)
            recommendations.append(f"Start {unhealthy_count} unhealthy ACGS services")

        # Constitutional compliance recommendations
        if not overall_summary.get("constitutional_compliance", False):
            recommendations.append(f"Ensure all tests validate constitutional hash: {CONSTITUTIONAL_HASH}")

        # Performance recommendations
        total_duration = overall_summary.get("total_duration_seconds", 0)
        if total_duration > 600:  # More than 10 minutes
            recommendations.append("Optimize test execution time with better parallelization")

        # General recommendations
        if not recommendations:
            recommendations.append("All tests passing - maintain current quality standards")
        else:
            recommendations.append("Implement automated test monitoring and alerting")
            recommendations.append("Set up continuous integration with test gates")

        return recommendations

    async def _save_test_results(self, results: Dict[str, Any]):
        """Save test results to files."""
        logger.info("💾 Saving test results...")

        try:
            # Create results directory
            results_dir = Path("reports/test_results")
            results_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
            filepath = results_dir / filename

            # Save results
            with open(filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"✅ Test results saved to {filepath}")

            # Also save latest results
            latest_filepath = results_dir / "latest_test_results.json"
            with open(latest_filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")


async def main():
    """Main function for running tests."""
    logger.info("🚀 ACGS Test Orchestrator Starting...")

    async with ACGSTestOrchestrator() as orchestrator:
        try:
            # Run all tests
            results = await orchestrator.run_all_tests()

            # Print summary
            overall = results.get("overall_summary", {})
            coverage = results.get("coverage_report", {})
            recommendations = results.get("recommendations", [])

            print("\n" + "="*60)
            print("🧪 ACGS TEST EXECUTION SUMMARY")
            print("="*60)
            print(f"Total Tests: {overall.get('total_tests', 0)}")
            print(f"Passed: {overall.get('passed_tests', 0)}")
            print(f"Failed: {overall.get('failed_tests', 0)}")
            print(f"Errors: {overall.get('error_tests', 0)}")
            print(f"Success Rate: {overall.get('success_rate_percentage', 0):.1f}%")
            print(f"Coverage: {coverage.get('total_coverage_percentage', 0):.1f}%")
            print(f"Duration: {overall.get('total_duration_seconds', 0):.1f}s")
            print(f"Status: {overall.get('overall_status', 'UNKNOWN')}")

            # Print target status
            print(f"\n🎯 TARGET STATUS:")
            print(f"Coverage Target (>{TEST_CONFIG['coverage_target']}%): {'✅' if coverage.get('meets_target', False) else '❌'}")
            print(f"Constitutional Compliance: {'✅' if overall.get('constitutional_compliance', False) else '❌'}")

            # Print recommendations
            if recommendations:
                print(f"\n📋 RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")

            print(f"\n🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
            print("="*60)

        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
