#!/usr/bin/env python3
"""
ACGS-1 Performance Testing - System Performance Validation
==========================================================

This script validates system performance post-reorganization with:
1. Load testing with concurrent requests
2. Response time analysis
3. Resource utilization monitoring
4. Throughput measurement
5. Stress testing
"""

import json
import logging
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("performance_testing.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ACGSPerformanceTester:
    """ACGS-1 Performance Testing Suite."""

    def __init__(self):
        self.services = [
            {"name": "auth_service", "port": 8000, "url": "http://localhost:8000"},
            {"name": "ac_service", "port": 8001, "url": "http://localhost:8001"},
            {"name": "integrity_service", "port": 8002, "url": "http://localhost:8002"},
            {"name": "fv_service", "port": 8003, "url": "http://localhost:8003"},
            {"name": "gs_service", "port": 8004, "url": "http://localhost:8004"},
            {"name": "pgc_service", "port": 8005, "url": "http://localhost:8005"},
            {"name": "ec_service", "port": 8006, "url": "http://localhost:8006"},
        ]
        self.test_results = []
        self.performance_targets = {
            "max_response_time_ms": 500,
            "avg_response_time_ms": 100,
            "min_success_rate": 95.0,
            "max_cpu_usage": 80.0,
            "max_memory_usage": 80.0,
        }

    def run_all_tests(self):
        """Run all performance tests."""
        logger.info("🚀 Starting ACGS-1 Performance Testing Suite")
        logger.info("=" * 60)

        # Test categories
        test_suites = [
            ("Baseline Response Time", self.test_baseline_response_time),
            ("Load Testing", self.test_load_performance),
            ("Concurrent Request Handling", self.test_concurrent_requests),
            ("Resource Utilization", self.test_resource_utilization),
            ("Throughput Measurement", self.test_throughput),
            ("Stress Testing", self.test_stress_performance),
        ]

        for suite_name, test_func in test_suites:
            logger.info(f"\n📋 Running {suite_name} Tests...")
            try:
                test_func()
            except Exception as e:
                logger.error(f"❌ Test suite {suite_name} failed: {e}")
                self.test_results.append(
                    {
                        "test_name": f"{suite_name}_suite",
                        "success": False,
                        "duration_ms": 0,
                        "details": {},
                        "error_message": str(e),
                    }
                )

        return self.test_results

    def test_baseline_response_time(self):
        """Test baseline response times for all services."""
        response_times = {}

        for service in self.services:
            times = []
            for i in range(10):  # 10 requests per service
                start_time = time.time()
                try:
                    response = requests.get(f"{service['url']}/health", timeout=5)
                    duration_ms = (time.time() - start_time) * 1000
                    if response.status_code == 200:
                        times.append(duration_ms)
                except Exception as e:
                    logger.warning(f"Baseline test failed for {service['name']}: {e}")

            if times:
                response_times[service["name"]] = {
                    "avg": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "median": statistics.median(times),
                    "p95": (
                        statistics.quantiles(times, n=20)[18]
                        if len(times) >= 20
                        else max(times)
                    ),
                }

        # Evaluate baseline performance
        avg_response_time = statistics.mean(
            [rt["avg"] for rt in response_times.values()]
        )
        max_response_time = max([rt["max"] for rt in response_times.values()])

        baseline_good = (
            avg_response_time < self.performance_targets["avg_response_time_ms"]
            and max_response_time < self.performance_targets["max_response_time_ms"]
        )

        self.test_results.append(
            {
                "test_name": "baseline_response_time",
                "success": baseline_good,
                "duration_ms": avg_response_time,
                "details": {
                    "service_response_times": response_times,
                    "overall_avg_ms": avg_response_time,
                    "overall_max_ms": max_response_time,
                    "target_met": baseline_good,
                },
            }
        )

        if baseline_good:
            logger.info(
                f"✅ Baseline response time test passed (avg: {avg_response_time:.2f}ms)"
            )
        else:
            logger.warning(
                f"⚠️ Baseline response time test warning (avg: {avg_response_time:.2f}ms)"
            )

    def test_load_performance(self):
        """Test performance under load with multiple concurrent requests."""

        def make_request(service_url):
            start_time = time.time()
            try:
                response = requests.get(f"{service_url}/health", timeout=10)
                duration_ms = (time.time() - start_time) * 1000
                return {
                    "success": response.status_code == 200,
                    "duration_ms": duration_ms,
                    "status_code": response.status_code,
                }
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                return {"success": False, "duration_ms": duration_ms, "error": str(e)}

        # Test with 20 concurrent requests per service
        concurrent_requests = 20
        all_results = []

        start_time = time.time()
        with ThreadPoolExecutor(
            max_workers=concurrent_requests * len(self.services)
        ) as executor:
            futures = []

            for service in self.services:
                for _ in range(concurrent_requests):
                    future = executor.submit(make_request, service["url"])
                    futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)

        total_duration = time.time() - start_time

        # Analyze results
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]

        success_rate = (len(successful_requests) / len(all_results)) * 100
        avg_response_time = (
            statistics.mean([r["duration_ms"] for r in successful_requests])
            if successful_requests
            else 0
        )

        load_test_passed = (
            success_rate >= self.performance_targets["min_success_rate"]
            and avg_response_time < self.performance_targets["max_response_time_ms"]
        )

        self.test_results.append(
            {
                "test_name": "load_performance",
                "success": load_test_passed,
                "duration_ms": total_duration * 1000,
                "details": {
                    "concurrent_requests": concurrent_requests * len(self.services),
                    "total_requests": len(all_results),
                    "successful_requests": len(successful_requests),
                    "failed_requests": len(failed_requests),
                    "success_rate": success_rate,
                    "avg_response_time_ms": avg_response_time,
                    "total_duration_s": total_duration,
                    "target_met": load_test_passed,
                },
            }
        )

        if load_test_passed:
            logger.info(
                f"✅ Load performance test passed (success rate: {success_rate:.1f}%)"
            )
        else:
            logger.warning(
                f"⚠️ Load performance test warning (success rate: {success_rate:.1f}%)"
            )

    def test_concurrent_requests(self):
        """Test concurrent request handling capability."""

        def concurrent_health_check():
            results = []
            for service in self.services:
                start_time = time.time()
                try:
                    response = requests.get(f"{service['url']}/health", timeout=5)
                    duration_ms = (time.time() - start_time) * 1000
                    results.append(
                        {
                            "service": service["name"],
                            "success": response.status_code == 200,
                            "duration_ms": duration_ms,
                        }
                    )
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    results.append(
                        {
                            "service": service["name"],
                            "success": False,
                            "duration_ms": duration_ms,
                            "error": str(e),
                        }
                    )
            return results

        # Run 10 concurrent batches
        concurrent_batches = 10
        all_batch_results = []

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=concurrent_batches) as executor:
            futures = [
                executor.submit(concurrent_health_check)
                for _ in range(concurrent_batches)
            ]

            for future in as_completed(futures):
                batch_results = future.result()
                all_batch_results.extend(batch_results)

        total_duration = time.time() - start_time

        # Analyze concurrent performance
        successful_requests = [r for r in all_batch_results if r["success"]]
        success_rate = (len(successful_requests) / len(all_batch_results)) * 100
        avg_response_time = (
            statistics.mean([r["duration_ms"] for r in successful_requests])
            if successful_requests
            else 0
        )

        concurrent_test_passed = (
            success_rate >= self.performance_targets["min_success_rate"]
        )

        self.test_results.append(
            {
                "test_name": "concurrent_requests",
                "success": concurrent_test_passed,
                "duration_ms": total_duration * 1000,
                "details": {
                    "concurrent_batches": concurrent_batches,
                    "total_requests": len(all_batch_results),
                    "successful_requests": len(successful_requests),
                    "success_rate": success_rate,
                    "avg_response_time_ms": avg_response_time,
                    "total_duration_s": total_duration,
                    "target_met": concurrent_test_passed,
                },
            }
        )

        if concurrent_test_passed:
            logger.info(
                f"✅ Concurrent requests test passed (success rate: {success_rate:.1f}%)"
            )
        else:
            logger.warning(
                f"⚠️ Concurrent requests test warning (success rate: {success_rate:.1f}%)"
            )

    def test_resource_utilization(self):
        """Test system resource utilization during load."""
        # Monitor system resources during a load test
        resource_data = []

        def monitor_resources():
            for _ in range(30):  # Monitor for 30 seconds
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                resource_data.append(
                    {
                        "timestamp": time.time(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory_percent,
                    }
                )

        def generate_load():
            # Generate load while monitoring
            for _ in range(50):  # 50 requests
                for service in self.services:
                    try:
                        requests.get(f"{service['url']}/health", timeout=2)
                    except:
                        pass
                time.sleep(0.1)  # Small delay between requests

        # Start monitoring and load generation
        monitor_thread = threading.Thread(target=monitor_resources)
        load_thread = threading.Thread(target=generate_load)

        monitor_thread.start()
        time.sleep(1)  # Start load after monitoring begins
        load_thread.start()

        monitor_thread.join()
        load_thread.join()

        if resource_data:
            avg_cpu = statistics.mean([r["cpu_percent"] for r in resource_data])
            max_cpu = max([r["cpu_percent"] for r in resource_data])
            avg_memory = statistics.mean([r["memory_percent"] for r in resource_data])
            max_memory = max([r["memory_percent"] for r in resource_data])

            resource_test_passed = (
                max_cpu < self.performance_targets["max_cpu_usage"]
                and max_memory < self.performance_targets["max_memory_usage"]
            )

            self.test_results.append(
                {
                    "test_name": "resource_utilization",
                    "success": resource_test_passed,
                    "duration_ms": 0,
                    "details": {
                        "avg_cpu_percent": avg_cpu,
                        "max_cpu_percent": max_cpu,
                        "avg_memory_percent": avg_memory,
                        "max_memory_percent": max_memory,
                        "monitoring_duration_s": len(resource_data),
                        "target_met": resource_test_passed,
                    },
                }
            )

            if resource_test_passed:
                logger.info(
                    f"✅ Resource utilization test passed (max CPU: {max_cpu:.1f}%, max Memory: {max_memory:.1f}%)"
                )
            else:
                logger.warning(
                    f"⚠️ Resource utilization test warning (max CPU: {max_cpu:.1f}%, max Memory: {max_memory:.1f}%)"
                )
        else:
            logger.error("❌ Resource utilization test failed - no data collected")

    def test_throughput(self):
        """Test system throughput (requests per second)."""
        duration_seconds = 10
        request_count = 0
        start_time = time.time()

        def make_requests():
            nonlocal request_count
            end_time = start_time + duration_seconds

            while time.time() < end_time:
                for service in self.services:
                    try:
                        response = requests.get(f"{service['url']}/health", timeout=2)
                        if response.status_code == 200:
                            request_count += 1
                    except:
                        pass

        # Use multiple threads to generate load
        threads = []
        for _ in range(5):  # 5 concurrent threads
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        actual_duration = time.time() - start_time
        throughput_rps = request_count / actual_duration

        # Target: at least 50 requests per second
        throughput_target = 50
        throughput_test_passed = throughput_rps >= throughput_target

        self.test_results.append(
            {
                "test_name": "throughput_measurement",
                "success": throughput_test_passed,
                "duration_ms": actual_duration * 1000,
                "details": {
                    "total_requests": request_count,
                    "duration_seconds": actual_duration,
                    "throughput_rps": throughput_rps,
                    "target_rps": throughput_target,
                    "target_met": throughput_test_passed,
                },
            }
        )

        if throughput_test_passed:
            logger.info(f"✅ Throughput test passed ({throughput_rps:.1f} RPS)")
        else:
            logger.warning(f"⚠️ Throughput test warning ({throughput_rps:.1f} RPS)")

    def test_stress_performance(self):
        """Test performance under stress conditions."""

        # Stress test with high concurrent load
        def stress_request(service_url):
            try:
                response = requests.get(f"{service_url}/health", timeout=1)
                return response.status_code == 200
            except:
                return False

        stress_duration = 15  # 15 seconds of stress
        concurrent_workers = 50
        successful_requests = 0
        total_requests = 0

        start_time = time.time()
        end_time = start_time + stress_duration

        with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            while time.time() < end_time:
                futures = []
                for service in self.services:
                    future = executor.submit(stress_request, service["url"])
                    futures.append(future)

                for future in as_completed(futures, timeout=2):
                    try:
                        if future.result():
                            successful_requests += 1
                        total_requests += 1
                    except:
                        total_requests += 1

        actual_duration = time.time() - start_time
        success_rate = (
            (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        )

        # Under stress, we expect at least 70% success rate
        stress_target = 70.0
        stress_test_passed = success_rate >= stress_target

        self.test_results.append(
            {
                "test_name": "stress_performance",
                "success": stress_test_passed,
                "duration_ms": actual_duration * 1000,
                "details": {
                    "stress_duration_s": actual_duration,
                    "concurrent_workers": concurrent_workers,
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "success_rate": success_rate,
                    "target_success_rate": stress_target,
                    "target_met": stress_test_passed,
                },
            }
        )

        if stress_test_passed:
            logger.info(
                f"✅ Stress performance test passed (success rate: {success_rate:.1f}%)"
            )
        else:
            logger.warning(
                f"⚠️ Stress performance test warning (success rate: {success_rate:.1f}%)"
            )

    def generate_report(self):
        """Generate comprehensive performance test report."""
        successful_tests = [t for t in self.test_results if t.get("success", False)]
        failed_tests = [t for t in self.test_results if not t.get("success", False)]

        report = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": (
                    (len(successful_tests) / len(self.test_results)) * 100
                    if self.test_results
                    else 0
                ),
            },
            "performance_targets": self.performance_targets,
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self):
        """Generate recommendations based on performance test results."""
        recommendations = []

        failed_tests = [t for t in self.test_results if not t.get("success", False)]
        if failed_tests:
            recommendations.append(
                f"Address {len(failed_tests)} failed performance tests"
            )

        # Check specific performance issues
        baseline_test = next(
            (
                t
                for t in self.test_results
                if t.get("test_name") == "baseline_response_time"
            ),
            None,
        )
        if baseline_test and not baseline_test.get("success", False):
            recommendations.append(
                "Optimize baseline response times - consider caching or code optimization"
            )

        load_test = next(
            (t for t in self.test_results if t.get("test_name") == "load_performance"),
            None,
        )
        if load_test and not load_test.get("success", False):
            recommendations.append(
                "Improve load handling capacity - consider horizontal scaling"
            )

        resource_test = next(
            (
                t
                for t in self.test_results
                if t.get("test_name") == "resource_utilization"
            ),
            None,
        )
        if resource_test and not resource_test.get("success", False):
            recommendations.append(
                "Optimize resource usage - check for memory leaks or CPU bottlenecks"
            )

        if not recommendations:
            recommendations.append(
                "All performance tests passed - system meets performance requirements"
            )

        return recommendations


def main():
    """Main execution function."""
    tester = ACGSPerformanceTester()

    try:
        # Run all performance tests
        results = tester.run_all_tests()

        # Generate and save report
        report = tester.generate_report()

        with open("performance_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 PERFORMANCE TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Successful: {report['summary']['successful_tests']}")
        logger.info(f"Failed: {report['summary']['failed_tests']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")

        if report["recommendations"]:
            logger.info("\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                logger.info(f"{i}. {rec}")

        logger.info("\n📄 Detailed report saved to: performance_test_report.json")

        # Exit with appropriate code
        if report["summary"]["success_rate"] >= 80:
            logger.info("✅ Performance testing completed successfully!")
            return 0
        logger.error("❌ Performance testing completed with issues")
        return 1

    except Exception as e:
        logger.error(f"Performance testing failed: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
