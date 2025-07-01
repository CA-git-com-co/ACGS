"""
Locust load testing configuration for DGM Service.

This file defines load testing scenarios to validate:
- SLA requirements (>99.9% uptime, <500ms response time)
- Concurrent user handling
- System behavior under stress
- Performance degradation patterns
"""

import json
import random
import time

from locust import HttpUser, between, events, task
from locust.runners import MasterRunner, WorkerRunner


class DGMServiceUser(HttpUser):
    """Simulates a user interacting with DGM Service."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a user starts."""
        # Simulate authentication if needed
        self.auth_token = None
        self.user_id = f"load_test_user_{random.randint(1000, 9999)}"

    @task(10)
    def health_check(self):
        """Health check endpoint - highest frequency."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(8)
    def get_metrics(self):
        """Get Prometheus metrics."""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics failed: {response.status_code}")

    @task(6)
    def get_status(self):
        """Get DGM service status."""
        with self.client.get("/api/v1/dgm/status", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "status" in data:
                        response.success()
                    else:
                        response.failure("Status response missing required fields")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status failed: {response.status_code}")

    @task(4)
    def get_performance_report(self):
        """Get performance report."""
        params = {
            "days": random.choice([1, 7, 30]),
            "service_name": random.choice(["dgm-service", None]),
        }

        with self.client.get(
            "/api/v1/dgm/performance", params=params, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Performance report failed: {response.status_code}")

    @task(3)
    def query_metrics(self):
        """Query specific metrics."""
        payload = {
            "metric_name": random.choice(
                [
                    "response_time",
                    "throughput",
                    "error_rate",
                    "cpu_usage",
                    "memory_usage",
                ]
            ),
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-12-31T23:59:59Z",
            "aggregation": random.choice(["avg", "max", "min", "sum"]),
            "service_filter": "dgm-service",
        }

        with self.client.post(
            "/api/v1/dgm/metrics/query", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics query failed: {response.status_code}")

    @task(2)
    def get_metrics_summary(self):
        """Get metrics summary."""
        params = {"hours": random.choice([1, 6, 24]), "service_name": "dgm-service"}

        with self.client.get(
            "/api/v1/dgm/metrics/summary", params=params, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics summary failed: {response.status_code}")

    @task(1)
    def trigger_improvement(self):
        """Trigger DGM improvement (low frequency, high impact)."""
        payload = {
            "target_service": "dgm-service",
            "improvement_type": "performance",
            "priority": random.choice(["low", "medium", "high"]),
            "description": f"Load test improvement request from {self.user_id}",
            "metadata": {
                "test_run": True,
                "user_id": self.user_id,
                "timestamp": time.time(),
            },
        }

        with self.client.post(
            "/api/v1/dgm/improve", json=payload, catch_response=True
        ) as response:
            if response.status_code in [200, 201, 202]:
                response.success()
            else:
                response.failure(f"Improvement trigger failed: {response.status_code}")


class HighLoadUser(HttpUser):
    """Simulates high-load scenarios for stress testing."""

    wait_time = between(0.1, 0.5)  # Very short wait times for stress testing

    @task(15)
    def rapid_health_checks(self):
        """Rapid health check requests."""
        self.client.get("/health")

    @task(10)
    def rapid_metrics(self):
        """Rapid metrics requests."""
        self.client.get("/metrics")

    @task(5)
    def rapid_status(self):
        """Rapid status requests."""
        self.client.get("/api/v1/dgm/status")


class SpikeTestUser(HttpUser):
    """Simulates traffic spikes for resilience testing."""

    wait_time = between(0, 1)

    def on_start(self):
        """Simulate sudden traffic spike."""
        # Make multiple rapid requests to simulate spike
        for _ in range(random.randint(5, 15)):
            self.client.get("/health")
            self.client.get("/metrics")

    @task
    def normal_operation(self):
        """Normal operation after spike."""
        self.client.get("/api/v1/dgm/status")


# Event handlers for custom metrics and reporting
@events.request.add_listener
def on_request(
    request_type, name, response_time, response_length, exception, context, **kwargs
):
    """Custom request handler for SLA validation."""
    if exception:
        print(f"Request failed: {name} - {exception}")
    elif response_time > 500:  # SLA violation: >500ms
        print(f"SLA VIOLATION: {name} took {response_time}ms (>500ms threshold)")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Starting DGM Service Load Test")
    print(f"Target host: {environment.host}")

    if isinstance(environment.runner, MasterRunner):
        print("Running in distributed mode (master)")
    elif isinstance(environment.runner, WorkerRunner):
        print("Running in distributed mode (worker)")
    else:
        print("Running in standalone mode")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops - validate SLA requirements."""
    stats = environment.runner.stats

    print("\n" + "=" * 60)
    print("LOAD TEST RESULTS - SLA VALIDATION")
    print("=" * 60)

    # Calculate overall statistics
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    success_rate = (
        ((total_requests - total_failures) / total_requests * 100)
        if total_requests > 0
        else 0
    )

    avg_response_time = stats.total.avg_response_time
    p95_response_time = stats.total.get_response_time_percentile(0.95)
    p99_response_time = stats.total.get_response_time_percentile(0.99)

    print(f"Total Requests: {total_requests}")
    print(f"Total Failures: {total_failures}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print(f"95th Percentile Response Time: {p95_response_time:.2f}ms")
    print(f"99th Percentile Response Time: {p99_response_time:.2f}ms")

    print("\n" + "-" * 40)
    print("SLA VALIDATION RESULTS")
    print("-" * 40)

    # SLA Requirement 1: >99.9% uptime (success rate)
    sla_uptime_met = success_rate >= 99.9
    print(
        f"Uptime SLA (>99.9%): {'✓ PASS' if sla_uptime_met else '✗ FAIL'} ({success_rate:.2f}%)"
    )

    # SLA Requirement 2: <500ms response time (95th percentile)
    sla_response_time_met = p95_response_time < 500
    print(
        f"Response Time SLA (<500ms P95): {'✓ PASS' if sla_response_time_met else '✗ FAIL'} ({p95_response_time:.2f}ms)"
    )

    # Additional performance indicators
    avg_response_good = avg_response_time < 250
    print(
        f"Average Response Time (<250ms): {'✓ GOOD' if avg_response_good else '⚠ WARNING'} ({avg_response_time:.2f}ms)"
    )

    p99_response_acceptable = p99_response_time < 1000
    print(
        f"99th Percentile Response Time (<1000ms): {'✓ GOOD' if p99_response_acceptable else '⚠ WARNING'} ({p99_response_time:.2f}ms)"
    )

    print("\n" + "-" * 40)
    print("ENDPOINT BREAKDOWN")
    print("-" * 40)

    # Show per-endpoint statistics
    for name, entry in stats.entries.items():
        if entry.num_requests > 0:
            endpoint_success_rate = (
                (entry.num_requests - entry.num_failures) / entry.num_requests * 100
            )
            print(f"{name}:")
            print(f"  Requests: {entry.num_requests}, Failures: {entry.num_failures}")
            print(f"  Success Rate: {endpoint_success_rate:.2f}%")
            print(f"  Avg Response Time: {entry.avg_response_time:.2f}ms")
            print(
                f"  P95 Response Time: {entry.get_response_time_percentile(0.95):.2f}ms"
            )

    # Overall SLA compliance
    overall_sla_met = sla_uptime_met and sla_response_time_met
    print(f"\nOVERALL SLA COMPLIANCE: {'✓ PASS' if overall_sla_met else '✗ FAIL'}")

    if not overall_sla_met:
        print(
            "\n⚠ WARNING: SLA requirements not met. Review system performance and scaling."
        )
    else:
        print("\n✓ SUCCESS: All SLA requirements met.")


# Custom load test scenarios
class LoadTestScenarios:
    """Predefined load test scenarios."""

    @staticmethod
    def normal_load():
        """Normal operational load."""
        return {
            "users": 50,
            "spawn_rate": 5,
            "run_time": "5m",
            "user_classes": [DGMServiceUser],
        }

    @staticmethod
    def high_load():
        """High load scenario."""
        return {
            "users": 200,
            "spawn_rate": 10,
            "run_time": "10m",
            "user_classes": [DGMServiceUser, HighLoadUser],
        }

    @staticmethod
    def stress_test():
        """Stress test scenario."""
        return {
            "users": 500,
            "spawn_rate": 25,
            "run_time": "15m",
            "user_classes": [DGMServiceUser, HighLoadUser],
        }

    @staticmethod
    def spike_test():
        """Traffic spike scenario."""
        return {
            "users": 100,
            "spawn_rate": 50,  # Rapid spawn for spike
            "run_time": "3m",
            "user_classes": [SpikeTestUser],
        }


# Usage examples:
# locust -f locustfile.py --host=http://localhost:8007
# locust -f locustfile.py --host=http://localhost:8007 --users 100 --spawn-rate 10 --run-time 5m
# locust -f locustfile.py --host=http://localhost:8007 --headless --users 200 --spawn-rate 20 --run-time 10m --html report.html
