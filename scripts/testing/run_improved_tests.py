#!/usr/bin/env python3
"""
ACGS Improved Test Runner
Constitutional Hash: cdd01ef066bc6cf2

Runs the improved ACGS test suite with proper configuration and reporting.
Targets >80% test coverage and >80% success rate.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Test configuration
TEST_CONFIG = {
    "target_coverage": 80.0,
    "target_success_rate": 80.0,
    "performance_targets": {
        "p99_latency_ms": 5.0,
        "throughput_rps": 100,
        "cache_hit_rate": 0.85,
        "constitutional_compliance": True,
    },
}


def setup_test_environment():
    """Set up the test environment with proper configuration."""
    print("🔧 Setting up test environment...")

    # Set environment variables
    os.environ["ACGS_ENVIRONMENT"] = "test"
    os.environ["ACGS_CONSTITUTIONAL_HASH"] = CONSTITUTIONAL_HASH
    os.environ["PYTHONPATH"] = str(Path.cwd())

    # Install missing dependencies if needed
    try:
        import aiohttp
        import coverage
        import groq
        import pytest_cov

        print("✅ All required dependencies are available")
    except ImportError as e:
        print(f"⚠️  Missing dependency: {e}")
        print("Installing missing dependencies...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "aiohttp>=3.9.0",
                "groq>=0.4.0",
                "coverage>=7.0.0",
                "pytest-cov>=4.1.0",
            ],
            check=True,
        )
        print("✅ Dependencies installed")


def run_test_category(category_name, test_path, timeout=300):
    """Run a specific test category with proper configuration."""
    print(f"\n🧪 Running {category_name} tests...")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        f"--junitxml=test_reports/{category_name}_results.xml",
        "--cov=services",
        "--cov-report=html:test_reports/htmlcov",
        "--cov-report=json:test_reports/coverage.json",
        "--disable-warnings",
    ]

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=Path.cwd()
        )

        duration = time.time() - start_time

        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "exit_code": -1,
            "duration": timeout,
            "stdout": "",
            "stderr": f"Test timed out after {timeout} seconds",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
    except Exception as e:
        return {
            "status": "error",
            "exit_code": -1,
            "duration": time.time() - start_time,
            "stdout": "",
            "stderr": str(e),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }


def run_comprehensive_tests():
    """Run the comprehensive ACGS test suite."""
    print("🚀 Starting ACGS Comprehensive Test Suite")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"🎯 Target Coverage: {TEST_CONFIG['target_coverage']}%")
    print(f"🎯 Target Success Rate: {TEST_CONFIG['target_success_rate']}%")

    # Ensure test reports directory exists
    os.makedirs("test_reports", exist_ok=True)

    # Test categories to run
    test_categories = [
        ("unit_tests_acgs_comprehensive", "tests/services/test_acgs_comprehensive.py"),
        (
            "unit_tests_constitutional_ai",
            "tests/services/test_constitutional_ai_service.py",
        ),
        ("unit_tests_authentication", "tests/services/test_authentication_service.py"),
        (
            "integration_service_integration",
            "tests/integration/test_acgs_service_integration.py",
        ),
        (
            "integration_end_to_end",
            "tests/integration/test_acgs_end_to_end_workflows.py",
        ),
        (
            "performance_validation",
            "tests/performance/test_acgs_performance_validation.py",
        ),
        ("performance_load_stress", "tests/performance/test_acgs_load_stress.py"),
    ]

    results = {}
    total_tests = 0
    passed_tests = 0

    start_time = time.time()

    for category_name, test_path in test_categories:
        if Path(test_path).exists():
            result = run_test_category(category_name, test_path)
            results[category_name] = result

            # Parse test results from stdout
            if "passed" in result["stdout"] or "failed" in result["stdout"]:
                # Extract test counts from pytest output
                lines = result["stdout"].split("\n")
                for line in lines:
                    if " passed" in line or " failed" in line:
                        # Simple parsing - could be improved
                        if result["status"] == "passed":
                            passed_tests += 1
                        total_tests += 1
                        break

            print(
                f"  {'✅' if result['status'] == 'passed' else '❌'} {category_name}: {result['status']}"
            )
        else:
            print(f"  ⏭️  Skipping {category_name}: {test_path} not found")

    total_duration = time.time() - start_time

    # Calculate success rate
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Generate comprehensive report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "success_rate": success_rate,
        "total_time": total_duration,
        "target_coverage": TEST_CONFIG["target_coverage"],
        "target_success_rate": TEST_CONFIG["target_success_rate"],
        "results_by_category": results,
        "performance_targets": TEST_CONFIG["performance_targets"],
    }

    # Save report
    with open("test_reports/improved_test_results.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n📊 Test Results Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Duration: {total_duration:.1f}s")
    print(f"   Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Check if targets are met
    if success_rate >= TEST_CONFIG["target_success_rate"]:
        print(
            f"✅ SUCCESS: Target success rate of {TEST_CONFIG['target_success_rate']}% achieved!"
        )
        return 0
    else:
        print(
            f"❌ FAILED: Success rate {success_rate:.1f}% below target {TEST_CONFIG['target_success_rate']}%"
        )
        return 1


def main():
    """Main entry point for the test runner."""
    try:
        setup_test_environment()
        return run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test run failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
