#!/usr/bin/env python3
"""
ACGS-1 Priority 2: Simple Performance Testing

This script performs focused performance testing for ACGS-1 services
to validate production readiness targets.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimplePerformanceTester:
    """Simple performance testing for ACGS-1."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.target_response_time = 500  # ms
        self.services = [8000, 8001, 8002, 8003, 8004, 8005, 8006]

    def execute_performance_tests(self) -> dict:
        """Execute performance tests."""
        logger.info("⚡ Starting ACGS-1 Simple Performance Tests")
        start_time = time.time()

        results = {
            "start_time": datetime.now().isoformat(),
            "target_response_time_ms": self.target_response_time,
            "tests": {},
        }

        try:
            # Test 1: Service Response Times
            logger.info("📊 Testing service response times...")
            response_test = self.test_service_response_times()
            results["tests"]["response_times"] = response_test

            # Test 2: Governance Workflow Performance
            logger.info("🏛️ Testing governance workflows...")
            workflow_test = self.test_governance_workflows()
            results["tests"]["governance_workflows"] = workflow_test

            # Test 3: Concurrent Request Handling
            logger.info("🔄 Testing concurrent requests...")
            concurrent_test = self.test_concurrent_requests()
            results["tests"]["concurrent_requests"] = concurrent_test

            # Test 4: System Resource Usage
            logger.info("💾 Checking system resources...")
            resource_test = self.check_system_resources()
            results["tests"]["system_resources"] = resource_test

            # Calculate overall results
            execution_time = time.time() - start_time
            results.update(
                {
                    "end_time": datetime.now().isoformat(),
                    "execution_time_seconds": execution_time,
                    "overall_success": self.evaluate_overall_performance(results),
                    "summary": self.generate_summary(results),
                }
            )

            # Save report
            self.save_report(results)

            return results

        except Exception as e:
            logger.error(f"❌ Performance testing failed: {e}")
            results["error"] = str(e)
            results["overall_success"] = False
            return results

    def test_service_response_times(self) -> dict:
        """Test response times for all services."""
        logger.info("📊 Testing service response times...")

        service_results = {}
        response_times = []

        for port in self.services:
            try:
                # Test service response time
                start = time.time()
                result = subprocess.run(
                    ["curl", "-s", "-f", f"http://localhost:{port}/health"],
                    capture_output=True,
                    timeout=10,
                )
                end = time.time()

                response_time = (end - start) * 1000  # Convert to ms
                response_times.append(response_time)

                service_results[f"service_{port}"] = {
                    "response_time_ms": round(response_time, 2),
                    "available": result.returncode == 0,
                    "meets_target": response_time < self.target_response_time,
                }

            except Exception as e:
                service_results[f"service_{port}"] = {
                    "available": False,
                    "error": str(e),
                    "meets_target": False,
                }

        # Calculate metrics
        available_services = sum(
            1 for s in service_results.values() if s.get("available", False)
        )
        services_meeting_target = sum(
            1 for s in service_results.values() if s.get("meets_target", False)
        )
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        return {
            "success": available_services >= 6
            and avg_response_time < self.target_response_time,
            "available_services": available_services,
            "total_services": len(self.services),
            "services_meeting_target": services_meeting_target,
            "avg_response_time_ms": round(avg_response_time, 2),
            "max_response_time_ms": (
                round(max(response_times), 2) if response_times else 0
            ),
            "service_results": service_results,
        }

    def test_governance_workflows(self) -> dict:
        """Test governance workflow endpoints."""
        logger.info("🏛️ Testing governance workflows...")

        # Test PGC service governance endpoints
        endpoints = [
            "/health",
            "/api/v1/policies",
            "/api/v1/compliance/check",
            "/api/v1/governance/status",
        ]

        workflow_results = {}

        for endpoint in endpoints:
            try:
                start = time.time()
                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        "-o",
                        "/dev/null",
                        "-w",
                        "%{http_code}",
                        f"http://localhost:8005{endpoint}",
                    ],
                    capture_output=True,
                    timeout=10,
                )
                end = time.time()

                response_time = (end - start) * 1000
                http_code = (
                    result.stdout.decode().strip() if result.stdout else "unknown"
                )

                workflow_results[endpoint] = {
                    "response_time_ms": round(response_time, 2),
                    "http_code": http_code,
                    "accessible": http_code
                    in ["200", "404"],  # 404 acceptable for unimplemented
                    "meets_target": response_time < self.target_response_time,
                }

            except Exception as e:
                workflow_results[endpoint] = {
                    "error": str(e),
                    "accessible": False,
                    "meets_target": False,
                }

        # Calculate workflow metrics
        accessible_workflows = sum(
            1 for w in workflow_results.values() if w.get("accessible", False)
        )
        workflows_meeting_target = sum(
            1 for w in workflow_results.values() if w.get("meets_target", False)
        )

        return {
            "success": accessible_workflows >= 2 and workflows_meeting_target >= 2,
            "accessible_workflows": accessible_workflows,
            "workflows_meeting_target": workflows_meeting_target,
            "total_workflows": len(endpoints),
            "workflow_results": workflow_results,
        }

    def test_concurrent_requests(self) -> dict:
        """Test concurrent request handling."""
        logger.info("🔄 Testing concurrent requests...")

        # Simple concurrent test using background processes
        concurrent_levels = [5, 10, 20]
        concurrent_results = {}

        for level in concurrent_levels:
            try:
                # Create multiple curl processes
                processes = []
                start_time = time.time()

                for _ in range(level):
                    proc = subprocess.Popen(
                        ["curl", "-s", "-f", "http://localhost:8005/health"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    processes.append(proc)

                # Wait for all processes to complete
                successful_requests = 0
                for proc in processes:
                    try:
                        proc.wait(timeout=10)
                        if proc.returncode == 0:
                            successful_requests += 1
                    except subprocess.TimeoutExpired:
                        proc.kill()

                end_time = time.time()
                total_time = end_time - start_time
                success_rate = successful_requests / level if level > 0 else 0

                concurrent_results[f"{level}_concurrent"] = {
                    "concurrent_requests": level,
                    "successful_requests": successful_requests,
                    "success_rate": round(success_rate, 2),
                    "total_time_seconds": round(total_time, 2),
                    "meets_target": success_rate >= 0.9,  # 90% success rate
                }

            except Exception as e:
                concurrent_results[f"{level}_concurrent"] = {
                    "error": str(e),
                    "meets_target": False,
                }

        # Find maximum supported concurrent level
        max_supported = 0
        for _level_key, result in concurrent_results.items():
            if result.get("meets_target", False):
                level = result.get("concurrent_requests", 0)
                max_supported = max(max_supported, level)

        return {
            "success": max_supported >= 10,  # At least 10 concurrent requests
            "max_supported_concurrent": max_supported,
            "concurrent_results": concurrent_results,
        }

    def check_system_resources(self) -> dict:
        """Check system resource usage."""
        logger.info("💾 Checking system resources...")

        resource_results = {}

        # Check memory usage
        try:
            result = subprocess.run(["free", "-m"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    mem_info = lines[1].split()
                    if len(mem_info) >= 3:
                        total_mem = int(mem_info[1])
                        used_mem = int(mem_info[2])
                        usage_percent = (used_mem / total_mem) * 100

                        resource_results["memory"] = {
                            "total_mb": total_mem,
                            "used_mb": used_mem,
                            "usage_percent": round(usage_percent, 1),
                            "healthy": usage_percent < 80,
                        }
        except Exception as e:
            resource_results["memory"] = {"error": str(e), "healthy": False}

        # Check disk usage
        try:
            result = subprocess.run(["df", "-h", "."], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    disk_info = lines[1].split()
                    if len(disk_info) >= 5:
                        usage_percent = int(disk_info[4].rstrip("%"))
                        resource_results["disk"] = {
                            "usage_percent": usage_percent,
                            "healthy": usage_percent < 80,
                        }
        except Exception as e:
            resource_results["disk"] = {"error": str(e), "healthy": False}

        # Check running processes
        try:
            result = subprocess.run(
                ["pgrep", "-f", "uvicorn"], capture_output=True, text=True
            )
            running_services = (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )

            resource_results["processes"] = {
                "running_services": running_services,
                "healthy": running_services >= 6,
            }
        except Exception as e:
            resource_results["processes"] = {"error": str(e), "healthy": False}

        # Calculate overall resource health
        healthy_resources = sum(
            1 for r in resource_results.values() if r.get("healthy", False)
        )

        return {
            "success": healthy_resources >= 2,
            "healthy_resources": healthy_resources,
            "total_resources": len(resource_results),
            "resource_results": resource_results,
        }

    def evaluate_overall_performance(self, results: dict) -> bool:
        """Evaluate overall performance success."""
        test_results = results.get("tests", {})

        # Check if all major tests passed
        response_success = test_results.get("response_times", {}).get("success", False)
        workflow_success = test_results.get("governance_workflows", {}).get(
            "success", False
        )
        concurrent_success = test_results.get("concurrent_requests", {}).get(
            "success", False
        )
        resource_success = test_results.get("system_resources", {}).get(
            "success", False
        )

        # Require at least 3 out of 4 tests to pass
        passed_tests = sum(
            [response_success, workflow_success, concurrent_success, resource_success]
        )
        return passed_tests >= 3

    def generate_summary(self, results: dict) -> dict:
        """Generate performance summary."""
        test_results = results.get("tests", {})

        # Extract key metrics
        avg_response_time = test_results.get("response_times", {}).get(
            "avg_response_time_ms", 0
        )
        available_services = test_results.get("response_times", {}).get(
            "available_services", 0
        )
        max_concurrent = test_results.get("concurrent_requests", {}).get(
            "max_supported_concurrent", 0
        )
        accessible_workflows = test_results.get("governance_workflows", {}).get(
            "accessible_workflows", 0
        )

        return {
            "avg_response_time_ms": avg_response_time,
            "available_services": f"{available_services}/7",
            "max_concurrent_requests": max_concurrent,
            "accessible_workflows": accessible_workflows,
            "meets_response_target": avg_response_time < self.target_response_time,
            "meets_availability_target": available_services >= 6,
            "meets_concurrent_target": max_concurrent >= 10,
        }

    def save_report(self, results: dict) -> None:
        """Save performance report."""
        report_file = f"priority2_performance_test_{int(time.time())}.json"
        report_path = self.project_root / "logs" / report_file

        # Ensure logs directory exists
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"📄 Performance report saved: {report_path}")


def main():
    """Main execution function."""
    tester = SimplePerformanceTester()
    results = tester.execute_performance_tests()

    if results.get("overall_success", False):
        print("✅ Performance testing completed successfully!")

        summary = results.get("summary", {})
        print("📊 Performance Summary:")
        print(
            f"  • Average Response Time: {summary.get('avg_response_time_ms', 0):.1f}ms (target: <500ms)"
        )
        print(f"  • Available Services: {summary.get('available_services', '0/7')}")
        print(
            f"  • Max Concurrent Requests: {summary.get('max_concurrent_requests', 0)}"
        )
        print(f"  • Accessible Workflows: {summary.get('accessible_workflows', 0)}")

        # Check targets
        if summary.get("meets_response_target", False):
            print("  ✅ Response time target met")
        else:
            print("  ❌ Response time target not met")

        if summary.get("meets_availability_target", False):
            print("  ✅ Availability target met")
        else:
            print("  ❌ Availability target not met")

        if summary.get("meets_concurrent_target", False):
            print("  ✅ Concurrent request target met")
        else:
            print("  ❌ Concurrent request target not met")

    else:
        print(
            f"❌ Performance testing failed: {results.get('error', 'Multiple test failures')}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
