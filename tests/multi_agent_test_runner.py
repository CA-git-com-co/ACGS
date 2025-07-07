"""
Comprehensive test runner for multi-agent coordination system.
Orchestrates unit, integration, performance, and E2E tests with reporting.
"""

# Constitutional Hash: cdd01ef066bc6cf2

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class MultiAgentTestRunner:
    """Comprehensive test runner for multi-agent coordination system"""

    def __init__(self, test_config: Optional[Dict[str, Any]] = None):
        self.test_config = test_config or self._default_config()
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_suites": {},
            "summary": {},
            "errors": [],
        }

    def _default_config(self) -> Dict[str, Any]:
        """Default test configuration"""
        return {
            "test_discovery": {
                "unit_tests": "tests/unit/multi_agent_coordination/",
                "integration_tests": "tests/integration/multi_agent_coordination/",
                "performance_tests": "tests/performance/multi_agent_coordination/",
                "e2e_tests": "tests/e2e/multi_agent_coordination/",
            },
            "test_execution": {
                "parallel_execution": True,
                "max_workers": 4,
                "timeout_seconds": 300,
                "retry_failed_tests": True,
                "max_retries": 2,
            },
            "reporting": {
                "generate_html_report": True,
                "generate_json_report": True,
                "coverage_analysis": True,
                "performance_metrics": True,
            },
            "output": {
                "reports_directory": "test_reports/multi_agent_coordination/",
                "log_level": "INFO",
                "verbose": False,
            },
        }

    async def run_all_tests(
        self,
        test_types: Optional[List[str]] = None,
        test_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run all or specified test types"""

        test_types = test_types or ["unit", "integration", "performance", "e2e"]

        print("🚀 Starting Multi-Agent Coordination Test Suite")
        print(f"Test types: {', '.join(test_types)}")
        print(f"Timestamp: {self.test_results['timestamp']}")
        print("-" * 60)

        # Ensure reports directory exists
        reports_dir = Path(self.test_config["output"]["reports_directory"])
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Run test suites
        if "unit" in test_types:
            await self._run_unit_tests(test_patterns)

        if "integration" in test_types:
            await self._run_integration_tests(test_patterns)

        if "performance" in test_types:
            await self._run_performance_tests(test_patterns)

        if "e2e" in test_types:
            await self._run_e2e_tests(test_patterns)

        # Generate summary
        self._generate_test_summary()

        # Generate reports
        if self.test_config["reporting"]["generate_json_report"]:
            self._generate_json_report()

        if self.test_config["reporting"]["generate_html_report"]:
            self._generate_html_report()

        # Print summary
        self._print_test_summary()

        return self.test_results

    async def _run_unit_tests(self, test_patterns: Optional[List[str]] = None):
        """Run unit tests for multi-agent coordination components"""
        print("\n📋 Running Unit Tests")
        print("-" * 40)

        unit_test_dir = self.test_config["test_discovery"]["unit_tests"]

        test_files = [
            "test_blackboard_service.py",
            "test_consensus_engine.py",
            "test_worker_agents.py",
            "test_performance_monitoring.py",
        ]

        suite_results = {
            "type": "unit",
            "start_time": datetime.utcnow().isoformat(),
            "tests": {},
            "stats": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0},
        }

        for test_file in test_files:
            if test_patterns and not any(
                pattern in test_file for pattern in test_patterns
            ):
                continue

            test_path = os.path.join(unit_test_dir, test_file)
            if not os.path.exists(test_path):
                print(f"⚠️  Test file not found: {test_path}")
                continue

            print(f"Running {test_file}...")

            # Run individual test file
            test_result = await self._run_pytest(
                test_path, test_type="unit", markers=["asyncio"]
            )

            suite_results["tests"][test_file] = test_result

            # Update stats
            suite_results["stats"]["total"] += test_result.get("total", 0)
            suite_results["stats"]["passed"] += test_result.get("passed", 0)
            suite_results["stats"]["failed"] += test_result.get("failed", 0)
            suite_results["stats"]["skipped"] += test_result.get("skipped", 0)
            suite_results["stats"]["errors"] += test_result.get("errors", 0)

            print(
                f"  ✅ {test_result.get('passed', 0)} passed, "
                f"❌ {test_result.get('failed', 0)} failed, "
                f"⏭️  {test_result.get('skipped', 0)} skipped"
            )

        suite_results["end_time"] = datetime.utcnow().isoformat()
        suite_results["duration_seconds"] = self._calculate_duration(
            suite_results["start_time"], suite_results["end_time"]
        )

        self.test_results["test_suites"]["unit"] = suite_results

        print(f"\n📊 Unit Tests Summary:")
        print(f"  Total: {suite_results['stats']['total']}")
        print(f"  Passed: {suite_results['stats']['passed']}")
        print(f"  Failed: {suite_results['stats']['failed']}")
        print(f"  Duration: {suite_results['duration_seconds']:.2f}s")

    async def _run_integration_tests(self, test_patterns: Optional[List[str]] = None):
        """Run integration tests for multi-agent coordination"""
        print("\n🔗 Running Integration Tests")
        print("-" * 40)

        integration_test_dir = self.test_config["test_discovery"]["integration_tests"]

        test_files = ["test_agent_coordination.py"]

        suite_results = {
            "type": "integration",
            "start_time": datetime.utcnow().isoformat(),
            "tests": {},
            "stats": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0},
        }

        for test_file in test_files:
            if test_patterns and not any(
                pattern in test_file for pattern in test_patterns
            ):
                continue

            test_path = os.path.join(integration_test_dir, test_file)
            if not os.path.exists(test_path):
                print(f"⚠️  Test file not found: {test_path}")
                continue

            print(f"Running {test_file}...")

            # Run integration test with longer timeout
            test_result = await self._run_pytest(
                test_path,
                test_type="integration",
                markers=["asyncio"],
                timeout=600,  # 10 minutes for integration tests
            )

            suite_results["tests"][test_file] = test_result

            # Update stats
            suite_results["stats"]["total"] += test_result.get("total", 0)
            suite_results["stats"]["passed"] += test_result.get("passed", 0)
            suite_results["stats"]["failed"] += test_result.get("failed", 0)
            suite_results["stats"]["skipped"] += test_result.get("skipped", 0)
            suite_results["stats"]["errors"] += test_result.get("errors", 0)

            print(
                f"  ✅ {test_result.get('passed', 0)} passed, "
                f"❌ {test_result.get('failed', 0)} failed, "
                f"⏭️  {test_result.get('skipped', 0)} skipped"
            )

        suite_results["end_time"] = datetime.utcnow().isoformat()
        suite_results["duration_seconds"] = self._calculate_duration(
            suite_results["start_time"], suite_results["end_time"]
        )

        self.test_results["test_suites"]["integration"] = suite_results

        print(f"\n📊 Integration Tests Summary:")
        print(f"  Total: {suite_results['stats']['total']}")
        print(f"  Passed: {suite_results['stats']['passed']}")
        print(f"  Failed: {suite_results['stats']['failed']}")
        print(f"  Duration: {suite_results['duration_seconds']:.2f}s")

    async def _run_performance_tests(self, test_patterns: Optional[List[str]] = None):
        """Run performance tests for multi-agent coordination"""
        print("\n⚡ Running Performance Tests")
        print("-" * 40)

        performance_test_dir = self.test_config["test_discovery"]["performance_tests"]

        test_files = ["test_coordination_performance.py"]

        suite_results = {
            "type": "performance",
            "start_time": datetime.utcnow().isoformat(),
            "tests": {},
            "stats": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0},
            "performance_metrics": {},
        }

        for test_file in test_files:
            if test_patterns and not any(
                pattern in test_file for pattern in test_patterns
            ):
                continue

            test_path = os.path.join(performance_test_dir, test_file)
            if not os.path.exists(test_path):
                print(f"⚠️  Test file not found: {test_path}")
                continue

            print(f"Running {test_file}...")

            # Run performance test with special markers
            test_result = await self._run_pytest(
                test_path,
                test_type="performance",
                markers=["asyncio", "performance"],
                timeout=900,  # 15 minutes for performance tests
                capture_performance=True,
            )

            suite_results["tests"][test_file] = test_result

            # Update stats
            suite_results["stats"]["total"] += test_result.get("total", 0)
            suite_results["stats"]["passed"] += test_result.get("passed", 0)
            suite_results["stats"]["failed"] += test_result.get("failed", 0)
            suite_results["stats"]["skipped"] += test_result.get("skipped", 0)
            suite_results["stats"]["errors"] += test_result.get("errors", 0)

            # Capture performance metrics
            if "performance_metrics" in test_result:
                suite_results["performance_metrics"][test_file] = test_result[
                    "performance_metrics"
                ]

            print(
                f"  ✅ {test_result.get('passed', 0)} passed, "
                f"❌ {test_result.get('failed', 0)} failed, "
                f"⏭️  {test_result.get('skipped', 0)} skipped"
            )

        suite_results["end_time"] = datetime.utcnow().isoformat()
        suite_results["duration_seconds"] = self._calculate_duration(
            suite_results["start_time"], suite_results["end_time"]
        )

        self.test_results["test_suites"]["performance"] = suite_results

        print(f"\n📊 Performance Tests Summary:")
        print(f"  Total: {suite_results['stats']['total']}")
        print(f"  Passed: {suite_results['stats']['passed']}")
        print(f"  Failed: {suite_results['stats']['failed']}")
        print(f"  Duration: {suite_results['duration_seconds']:.2f}s")

    async def _run_e2e_tests(self, test_patterns: Optional[List[str]] = None):
        """Run end-to-end tests for governance scenarios"""
        print("\n🎯 Running End-to-End Tests")
        print("-" * 40)

        e2e_test_dir = self.test_config["test_discovery"]["e2e_tests"]

        test_files = ["test_governance_scenarios.py"]

        suite_results = {
            "type": "e2e",
            "start_time": datetime.utcnow().isoformat(),
            "tests": {},
            "stats": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0},
        }

        for test_file in test_files:
            if test_patterns and not any(
                pattern in test_file for pattern in test_patterns
            ):
                continue

            test_path = os.path.join(e2e_test_dir, test_file)
            if not os.path.exists(test_path):
                print(f"⚠️  Test file not found: {test_path}")
                continue

            print(f"Running {test_file}...")

            # Run E2E test with extended timeout
            test_result = await self._run_pytest(
                test_path,
                test_type="e2e",
                markers=["asyncio", "e2e"],
                timeout=1200,  # 20 minutes for E2E tests
            )

            suite_results["tests"][test_file] = test_result

            # Update stats
            suite_results["stats"]["total"] += test_result.get("total", 0)
            suite_results["stats"]["passed"] += test_result.get("passed", 0)
            suite_results["stats"]["failed"] += test_result.get("failed", 0)
            suite_results["stats"]["skipped"] += test_result.get("skipped", 0)
            suite_results["stats"]["errors"] += test_result.get("errors", 0)

            print(
                f"  ✅ {test_result.get('passed', 0)} passed, "
                f"❌ {test_result.get('failed', 0)} failed, "
                f"⏭️  {test_result.get('skipped', 0)} skipped"
            )

        suite_results["end_time"] = datetime.utcnow().isoformat()
        suite_results["duration_seconds"] = self._calculate_duration(
            suite_results["start_time"], suite_results["end_time"]
        )

        self.test_results["test_suites"]["e2e"] = suite_results

        print(f"\n📊 End-to-End Tests Summary:")
        print(f"  Total: {suite_results['stats']['total']}")
        print(f"  Passed: {suite_results['stats']['passed']}")
        print(f"  Failed: {suite_results['stats']['failed']}")
        print(f"  Duration: {suite_results['duration_seconds']:.2f}s")

    async def _run_pytest(
        self,
        test_path: str,
        test_type: str,
        markers: Optional[List[str]] = None,
        timeout: int = 300,
        capture_performance: bool = False,
    ) -> Dict[str, Any]:
        """Run pytest on a specific test file or directory"""

        cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short"]

        # Add markers
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])

        # Add coverage for unit tests
        if test_type == "unit":
            cmd.extend(
                [
                    "--cov=services.core.multi_agent_coordinator",
                    "--cov=services.core.worker_agents",
                    "--cov=services.core.consensus_engine",
                    "--cov=services.shared.blackboard",
                    "--cov-report=term-missing",
                    "--cov-report=json",
                ]
            )

        # Add performance capture
        if capture_performance:
            cmd.extend(["--benchmark-json=benchmark_results.json"])

        # Run pytest
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 60,  # Add buffer to subprocess timeout
            )

            duration = time.time() - start_time

            # Parse pytest output
            return self._parse_pytest_output(result, duration, capture_performance)

        except subprocess.TimeoutExpired:
            return {
                "total": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "errors": 0,
                "duration": timeout,
                "status": "timeout",
                "error": f"Test timed out after {timeout} seconds",
            }
        except Exception as e:
            return {
                "total": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "errors": 1,
                "duration": time.time() - start_time,
                "status": "error",
                "error": str(e),
            }

    def _parse_pytest_output(
        self,
        result: subprocess.CompletedProcess,
        duration: float,
        capture_performance: bool = False,
    ) -> Dict[str, Any]:
        """Parse pytest output to extract test results"""

        output = result.stdout + result.stderr

        # Parse test counts from pytest output
        test_result = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration": duration,
            "exit_code": result.returncode,
            "output": output,
        }

        # Extract test counts from pytest summary line
        lines = output.split("\n")
        for line in lines:
            # Look for the final summary line like "======== 6 failed, 4 passed, 1 skipped, 60 warnings, 10 errors in 2.28s ========"
            if (
                "======" in line
                and " in " in line
                and (
                    "passed" in line
                    or "failed" in line
                    or "error" in line
                    or "skipped" in line
                )
            ):
                # Parse the summary line
                import re

                # Extract numbers followed by test result words
                passed_match = re.search(r"(\d+)\s+passed", line)
                failed_match = re.search(r"(\d+)\s+failed", line)
                skipped_match = re.search(r"(\d+)\s+skipped", line)
                error_match = re.search(r"(\d+)\s+error", line)

                if passed_match:
                    test_result["passed"] = int(passed_match.group(1))
                if failed_match:
                    test_result["failed"] = int(failed_match.group(1))
                if skipped_match:
                    test_result["skipped"] = int(skipped_match.group(1))
                if error_match:
                    test_result["errors"] = int(error_match.group(1))
                break

        test_result["total"] = (
            test_result["passed"]
            + test_result["failed"]
            + test_result["skipped"]
            + test_result["errors"]
        )

        # Add performance metrics if requested
        if capture_performance and os.path.exists("benchmark_results.json"):
            try:
                with open("benchmark_results.json", "r") as f:
                    benchmark_data = json.load(f)
                    test_result["performance_metrics"] = benchmark_data
                os.remove("benchmark_results.json")  # Clean up
            except Exception:
                pass  # Ignore benchmark parsing errors

        # Determine status
        if result.returncode == 0:
            test_result["status"] = "success"
        elif test_result["failed"] > 0 or test_result["errors"] > 0:
            test_result["status"] = "failed"
        else:
            test_result["status"] = "unknown"

        return test_result

    def _generate_test_summary(self):
        """Generate overall test summary"""
        summary = {
            "total_suites": len(self.test_results["test_suites"]),
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "total_duration": 0.0,
            "success_rate": 0.0,
            "suite_results": {},
        }

        for suite_name, suite_data in self.test_results["test_suites"].items():
            stats = suite_data["stats"]
            duration = suite_data.get("duration_seconds", 0)

            summary["total_tests"] += stats["total"]
            summary["total_passed"] += stats["passed"]
            summary["total_failed"] += stats["failed"]
            summary["total_skipped"] += stats["skipped"]
            summary["total_errors"] += stats["errors"]
            summary["total_duration"] += duration

            suite_success_rate = (
                stats["passed"] / stats["total"] if stats["total"] > 0 else 0.0
            )

            summary["suite_results"][suite_name] = {
                "tests": stats["total"],
                "passed": stats["passed"],
                "failed": stats["failed"],
                "success_rate": suite_success_rate,
                "duration": duration,
            }

        if summary["total_tests"] > 0:
            summary["success_rate"] = summary["total_passed"] / summary["total_tests"]

        self.test_results["summary"] = summary

    def _generate_json_report(self):
        """Generate JSON test report"""
        reports_dir = Path(self.test_config["output"]["reports_directory"])

        report_file = (
            reports_dir
            / f"multi_agent_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        print(f"\n📄 JSON report saved: {report_file}")

    def _generate_html_report(self):
        """Generate HTML test report"""
        reports_dir = Path(self.test_config["output"]["reports_directory"])

        report_file = (
            reports_dir
            / f"multi_agent_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )

        html_content = self._create_html_report()

        with open(report_file, "w") as f:
            f.write(html_content)

        print(f"📄 HTML report saved: {report_file}")

    def _create_html_report(self) -> str:
        """Create HTML report content"""
        summary = self.test_results["summary"]

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Multi-Agent Coordination Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
                .suite {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
                .suite-header {{ background: #f9f9f9; padding: 10px; font-weight: bold; }}
                .suite-content {{ padding: 15px; }}
                .passed {{ color: #28a745; }}
                .failed {{ color: #dc3545; }}
                .skipped {{ color: #ffc107; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Multi-Agent Coordination Test Report</h1>
                <p>Generated: {self.test_results['timestamp']}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>{summary['total_tests']}</h3>
                    <p>Total Tests</p>
                </div>
                <div class="metric">
                    <h3 class="passed">{summary['total_passed']}</h3>
                    <p>Passed</p>
                </div>
                <div class="metric">
                    <h3 class="failed">{summary['total_failed']}</h3>
                    <p>Failed</p>
                </div>
                <div class="metric">
                    <h3>{summary['success_rate']:.1%}</h3>
                    <p>Success Rate</p>
                </div>
                <div class="metric">
                    <h3>{summary['total_duration']:.1f}s</h3>
                    <p>Duration</p>
                </div>
            </div>
        """

        # Add suite details
        for suite_name, suite_data in self.test_results["test_suites"].items():
            stats = suite_data["stats"]
            html += f"""
            <div class="suite">
                <div class="suite-header">{suite_name.title()} Tests</div>
                <div class="suite-content">
                    <p><strong>Total:</strong> {stats['total']}</p>
                    <p><span class="passed">Passed: {stats['passed']}</span></p>
                    <p><span class="failed">Failed: {stats['failed']}</span></p>
                    <p><span class="skipped">Skipped: {stats['skipped']}</span></p>
                    <p><strong>Duration:</strong> {suite_data.get('duration_seconds', 0):.2f}s</p>
                </div>
            </div>
            """

        html += """
        </body>
        </html>
        """

        return html

    def _print_test_summary(self):
        """Print comprehensive test summary"""
        summary = self.test_results["summary"]

        print("\n" + "=" * 60)
        print("🎯 MULTI-AGENT COORDINATION TEST SUMMARY")
        print("=" * 60)

        print(f"📊 Overall Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['total_passed']}")
        print(f"   ❌ Failed: {summary['total_failed']}")
        print(f"   ⏭️  Skipped: {summary['total_skipped']}")
        print(f"   🚨 Errors: {summary['total_errors']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1%}")
        print(f"   ⏱️  Total Duration: {summary['total_duration']:.2f}s")

        print(f"\n📋 Suite Breakdown:")
        for suite_name, suite_results in summary["suite_results"].items():
            status_icon = (
                "✅"
                if suite_results["success_rate"] >= 0.8
                else "⚠️" if suite_results["success_rate"] >= 0.5 else "❌"
            )
            print(
                f"   {status_icon} {suite_name.title()}: {suite_results['passed']}/{suite_results['tests']} "
                f"({suite_results['success_rate']:.1%}) in {suite_results['duration']:.2f}s"
            )

        # Overall status
        if summary["success_rate"] >= 0.95:
            print(
                f"\n🎉 EXCELLENT: Multi-agent coordination system is production ready!"
            )
        elif summary["success_rate"] >= 0.8:
            print(
                f"\n✅ GOOD: Multi-agent coordination system is mostly ready with minor issues"
            )
        elif summary["success_rate"] >= 0.6:
            print(
                f"\n⚠️  WARNING: Multi-agent coordination system has significant issues"
            )
        else:
            print(f"\n❌ CRITICAL: Multi-agent coordination system has major failures")

        print("=" * 60)

    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate duration between two ISO timestamps"""
        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            return (end - start).total_seconds()
        except Exception:
            return 0.0


async def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description="Multi-Agent Coordination Test Runner")

    parser.add_argument(
        "--test-types",
        nargs="+",
        choices=["unit", "integration", "performance", "e2e"],
        default=["unit", "integration"],
        help="Test types to run",
    )

    parser.add_argument(
        "--test-patterns", nargs="+", help="Test file patterns to match"
    )

    parser.add_argument("--config", help="Path to test configuration JSON file")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Load configuration
    test_config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, "r") as f:
            test_config = json.load(f)

    # Create test runner
    runner = MultiAgentTestRunner(test_config)

    if args.verbose:
        runner.test_config["output"]["verbose"] = True

    # Run tests
    results = await runner.run_all_tests(
        test_types=args.test_types, test_patterns=args.test_patterns
    )

    # Exit with appropriate code
    success_rate = results["summary"]["success_rate"]
    if success_rate >= 0.8:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    asyncio.run(main())
