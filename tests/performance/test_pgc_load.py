"""
ACGS-1 PGC Performance Load Test

Locust-based load testing for the Policy Governance Controller (PGC) service.
Tests policy decision endpoints against ultra-low latency targets (<25ms for 95% of requests).

Usage:
    # Install dependencies
    pip install locust

    # Run load test
    locust -f tests/performance/pgc_load_test.py --host=http://localhost:8003

    # Run with specific parameters
    locust -f tests/performance/pgc_load_test.py --host=http://localhost:8003 --users=50 --spawn-rate=5 --run-time=300s

Requirements:
    - PGC Service running on port 8003
    - Target: <25ms latency for 95% of requests
    - ACGS constitutional governance compliance
"""

import json
import logging
import os
import random
import time
from datetime import datetime

from locust import HttpUser, between, events, task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pgc_load_test")

# Performance targets from ACGS constitutional governance standards
LATENCY_TARGET_MS = 25  # <25ms for 95% of requests
THROUGHPUT_TARGET_RPS = 1000  # >1000 requests per second
AVAILABILITY_TARGET = 99.5  # >99.5% availability


class PGCLoadTestUser(HttpUser):
    """
    Simulates realistic policy decision requests against the PGC service.

    The PGC (Policy Governance Controller) enforces governance policies in real-time
    using the Open Policy Agent (OPA) and must meet ultra-low latency requirements.
    """

    host = "http://localhost:8003"  # Policy Governance Service runs on port 8003
    wait_time = between(0.001, 0.005)  # Minimal wait to stress test high throughput

    def on_start(self):
        """Initialize user session with authentication if needed."""
        self.user_id = f"load_test_user_{random.randint(1, 10000)}"
        self.session_start = time.time()
        logger.info(f"Starting load test session for user {self.user_id}")

    @task(8)  # 80% of requests - primary policy optimization endpoint
    def optimize_policy(self):
        """
        Test the main policy optimization endpoint with realistic payloads.

        This endpoint is the core of the PGC service and must meet the
        <25ms latency target for constitutional governance compliance.
        """
        # Generate realistic policy decision payload
        payload = {
            "user_id": self.user_id,
            "resource": f"resource_{random.randint(1, 100)}",
            "action": random.choice(["read", "write", "delete", "update", "execute"]),
            "context": {
                "user": {
                    "id": random.randint(1, 500),
                    "role": random.choice(
                        ["admin", "user", "guest", "moderator", "auditor"]
                    ),
                    "department": random.choice(
                        ["engineering", "governance", "compliance", "security"]
                    ),
                    "clearance_level": random.choice(
                        ["public", "internal", "confidential", "restricted"]
                    ),
                },
                "resource": {
                    "id": random.randint(1, 1000),
                    "type": random.choice(
                        ["document", "image", "record", "policy", "constitution"]
                    ),
                    "classification": random.choice(
                        ["public", "internal", "sensitive", "critical"]
                    ),
                    "owner": f"owner_{random.randint(1, 100)}",
                },
                "action": {
                    "type": random.choice(
                        ["access", "modify", "remove", "approve", "audit"]
                    ),
                    "timestamp": datetime.now().isoformat(),
                    "source_ip": f"192.168.1.{random.randint(1, 254)}",
                },
                "environment": {
                    "location": random.choice(
                        ["HQ", "Branch", "Remote", "Cloud", "Edge"]
                    ),
                    "time_of_day": random.choice(
                        ["business_hours", "after_hours", "weekend"]
                    ),
                    "security_level": random.choice(
                        ["standard", "elevated", "high", "critical"]
                    ),
                },
            },
            "optimization_level": random.choice(["STANDARD", "ENHANCED", "ULTRA"]),
            "constitutional_compliance": True,
            "audit_required": random.choice([True, False]),
        }

        start_time = time.time()

        with self.client.post(
            "/optimize",
            json=payload,
            catch_response=True,
            headers={"Content-Type": "application/json"},
        ) as response:

            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                # Check if latency meets constitutional governance target
                target_met = latency_ms <= LATENCY_TARGET_MS

                # Log performance metrics
                logger.info(
                    f"Policy optimization: {latency_ms:.2f}ms | Target met: {target_met}"
                )

                # Mark as failure if latency target not met (for Locust statistics)
                if not target_met:
                    response.failure(
                        f"Latency {latency_ms:.2f}ms exceeds target {LATENCY_TARGET_MS}ms"
                    )

                # Validate response structure for constitutional compliance
                try:
                    result = response.json()
                    required_fields = [
                        "decision",
                        "policy_id",
                        "timestamp",
                        "audit_trail",
                    ]
                    if not all(field in result for field in required_fields):
                        response.failure(
                            "Response missing required constitutional governance fields"
                        )
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")

            elif response.status_code == 429:
                # Rate limiting - expected under high load
                logger.warning(f"Rate limited: {response.status_code}")
                response.failure("Rate limited")
            else:
                logger.error(
                    f"Request failed: {response.status_code} - {response.text}"
                )
                response.failure(f"HTTP {response.status_code}")

    @task(1)  # 10% of requests - health check endpoint
    def health_check(self):
        """Test service health endpoint for availability monitoring."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")

    @task(1)  # 10% of requests - metrics endpoint
    def get_metrics(self):
        """Test metrics endpoint for monitoring and observability."""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Metrics endpoint failed: {response.status_code}")


class PGCStressTestUser(HttpUser):
    """
    High-intensity stress testing user for extreme load scenarios.

    Used to test system behavior under constitutional governance emergency scenarios
    where policy decisions must be made rapidly under extreme load.
    """

    host = "http://localhost:8003"
    wait_time = between(0.0001, 0.001)  # Extremely aggressive load
    weight = 1  # Lower weight - only used for stress testing

    @task
    def rapid_fire_policy_decisions(self):
        """Rapid-fire policy decisions to test system limits."""
        payload = {
            "user_id": f"stress_user_{random.randint(1, 1000)}",
            "resource": f"critical_resource_{random.randint(1, 10)}",
            "action": "emergency_access",
            "context": {
                "emergency": True,
                "priority": "CRITICAL",
                "constitutional_override": False,
            },
            "optimization_level": "ULTRA",
        }

        start_time = time.time()
        with self.client.post(
            "/optimize", json=payload, catch_response=True
        ) as response:
            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                if (
                    latency_ms > LATENCY_TARGET_MS * 2
                ):  # Allow 2x target for stress test
                    response.failure(f"Stress test latency {latency_ms:.2f}ms too high")
            else:
                response.failure(f"Stress test failed: {response.status_code}")


# Event handlers for detailed performance reporting
@events.request.add_listener
def on_request(
    request_type, name, response_time, response_length, exception, context, **kwargs
):
    """Log detailed request metrics for constitutional governance audit trail."""
    if exception:
        logger.error(f"Request failed: {request_type} {name} - {exception}")
    elif response_time > LATENCY_TARGET_MS:
        logger.warning(
            f"Latency target missed: {request_type} {name} - {response_time:.2f}ms"
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize performance test with constitutional governance logging."""
    logger.info("🔒 Starting ACGS-1 PGC Performance Load Test")
    logger.info(f"📊 Target Latency: <{LATENCY_TARGET_MS}ms for 95% of requests")
    logger.info(f"🚀 Target Throughput: >{THROUGHPUT_TARGET_RPS} RPS")
    logger.info(f"⚡ Target Availability: >{AVAILABILITY_TARGET}%")
    logger.info("🏛️ Constitutional Governance Compliance: ENFORCED")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate final performance report for constitutional governance audit."""
    stats = environment.stats

    # Calculate key metrics
    total_requests = stats.total.num_requests
    failed_requests = stats.total.num_failures
    availability = (
        ((total_requests - failed_requests) / total_requests * 100)
        if total_requests > 0
        else 0
    )

    # Generate compliance report
    compliance_report = {
        "test_completion_time": datetime.now().isoformat(),
        "total_requests": total_requests,
        "failed_requests": failed_requests,
        "availability_percent": round(availability, 2),
        "average_response_time_ms": round(stats.total.avg_response_time, 2),
        "median_response_time_ms": round(stats.total.median_response_time, 2),
        "p95_response_time_ms": round(
            stats.total.get_response_time_percentile(0.95), 2
        ),
        "p99_response_time_ms": round(
            stats.total.get_response_time_percentile(0.99), 2
        ),
        "constitutional_compliance": {
            "latency_target_met": stats.total.get_response_time_percentile(0.95)
            <= LATENCY_TARGET_MS,
            "availability_target_met": availability >= AVAILABILITY_TARGET,
            "zero_critical_failures": failed_requests == 0,
        },
    }

    # Save compliance report
    os.makedirs("logs", exist_ok=True)
    report_file = (
        f"logs/pgc_load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_file, "w") as f:
        json.dump(compliance_report, f, indent=2)

    logger.info("🏁 ACGS-1 PGC Performance Load Test Completed")
    logger.info(f"📊 Compliance Report: {report_file}")
    logger.info(
        f"⚡ P95 Latency: {compliance_report['p95_response_time_ms']}ms (Target: <{LATENCY_TARGET_MS}ms)"
    )
    logger.info(
        f"🎯 Availability: {compliance_report['availability_percent']}% (Target: >{AVAILABILITY_TARGET}%)"
    )

    # Constitutional governance compliance check
    compliance = compliance_report["constitutional_compliance"]
    if all(compliance.values()):
        logger.info("✅ CONSTITUTIONAL GOVERNANCE COMPLIANCE: PASSED")
    else:
        logger.error("❌ CONSTITUTIONAL GOVERNANCE COMPLIANCE: FAILED")
        for check, passed in compliance.items():
            if not passed:
                logger.error(f"   ❌ {check}: FAILED")
