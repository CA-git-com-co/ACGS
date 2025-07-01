#!/usr/bin/env python3
"""
Constitutional Trainer Service Load Testing with Locust

This script provides comprehensive load testing for the Constitutional Trainer Service
using Locust framework with detailed performance monitoring and HPA validation.

Usage:
    # Basic load test
    locust -f tests/load/constitutional_trainer_locust.py --host=http://constitutional-trainer:8000

    # Headless mode with specific user count and duration
    locust -f tests/load/constitutional_trainer_locust.py --host=http://constitutional-trainer:8000 \
           --users 100 --spawn-rate 10 --run-time 10m --headless

    # With custom configuration
    POLICY_ENGINE_URL=http://policy-engine:8001 \
    locust -f tests/load/constitutional_trainer_locust.py --host=http://constitutional-trainer:8000
"""

import json
import os
import random
import time
import uuid
from typing import Any, Dict, List

import requests
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


class ConstitutionalTrainerUser(HttpUser):
    """Simulates a user interacting with the Constitutional Trainer Service."""

    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)

    def on_start(self):
        """Initialize user session."""
        self.policy_engine_url = os.getenv(
            "POLICY_ENGINE_URL", "http://policy-engine:8001"
        )
        self.auth_token = "load-test-token"
        self.user_id = f"load-test-user-{uuid.uuid4().hex[:8]}"

        # Performance tracking
        self.training_requests = 0
        self.policy_evaluations = 0
        self.errors = 0

    @task(5)  # Weight: 5 (most common operation)
    def submit_training_request(self):
        """Submit a constitutional training request."""
        training_request = self._generate_training_request()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        start_time = time.time()

        with self.client.post(
            "/api/v1/train",
            json=training_request,
            headers=headers,
            catch_response=True,
            name="submit_training_request",
        ) as response:

            latency = (time.time() - start_time) * 1000  # Convert to ms

            if response.status_code in [200, 202]:
                self.training_requests += 1

                # Validate response structure
                try:
                    result = response.json()
                    if "training_id" not in result:
                        response.failure("Missing training_id in response")
                    else:
                        # Check training status after submission
                        self._check_training_status(result["training_id"])

                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")

                # Performance assertion
                if latency > 5000:  # 5 seconds
                    response.failure(f"Training request too slow: {latency:.2f}ms")

            else:
                self.errors += 1
                response.failure(f"Training request failed: {response.status_code}")

    @task(3)  # Weight: 3
    def evaluate_policy(self):
        """Test policy evaluation endpoint."""
        policy_request = self._generate_policy_request()

        headers = {"Content-Type": "application/json"}

        start_time = time.time()

        # Use requests directly for policy engine (different host)
        try:
            response = requests.post(
                f"{self.policy_engine_url}/v1/evaluate",
                json=policy_request,
                headers=headers,
                timeout=5,
            )

            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                self.policy_evaluations += 1

                # Validate response structure
                try:
                    result = response.json()
                    if "allow" not in result:
                        self._record_failure(
                            "policy_evaluation", "Missing allow field in response"
                        )

                    # Performance assertion for policy evaluation
                    if latency > 25:  # 25ms target
                        self._record_failure(
                            "policy_evaluation",
                            f"Policy evaluation too slow: {latency:.2f}ms",
                        )
                    else:
                        self._record_success("policy_evaluation", latency)

                except json.JSONDecodeError:
                    self._record_failure("policy_evaluation", "Invalid JSON response")

            else:
                self.errors += 1
                self._record_failure(
                    "policy_evaluation",
                    f"Policy evaluation failed: {response.status_code}",
                )

        except requests.RequestException as e:
            self.errors += 1
            self._record_failure(
                "policy_evaluation", f"Policy evaluation error: {str(e)}"
            )

    @task(2)  # Weight: 2
    def check_service_health(self):
        """Check service health endpoints."""
        with self.client.get(
            "/health", catch_response=True, name="health_check"
        ) as response:
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    if health_data.get("status") != "healthy":
                        response.failure("Service reports unhealthy status")
                except json.JSONDecodeError:
                    response.failure("Invalid health check response")
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(1)  # Weight: 1 (least common)
    def get_metrics(self):
        """Retrieve Prometheus metrics."""
        with self.client.get(
            "/metrics", catch_response=True, name="get_metrics"
        ) as response:
            if response.status_code == 200:
                # Validate metrics format
                metrics_text = response.text
                if "constitutional_compliance_score" not in metrics_text:
                    response.failure("Missing expected metrics")
            else:
                response.failure(f"Metrics endpoint failed: {response.status_code}")

    def _generate_training_request(self) -> Dict[str, Any]:
        """Generate a realistic training request."""
        model_name = f"load-test-model-{random.randint(1000, 9999)}"

        training_data = [
            {
                "prompt": random.choice(
                    [
                        "What are the key principles of constitutional AI?",
                        "How should AI systems handle sensitive data?",
                        "What is the role of human oversight in AI governance?",
                        "How can AI systems ensure fairness and non-discrimination?",
                        "What are the ethical considerations for AI decision-making?",
                    ]
                ),
                "response": random.choice(
                    [
                        "Constitutional AI focuses on training AI systems to be helpful, harmless, and honest.",
                        "AI systems should implement strong privacy protections and transparent practices.",
                        "Human oversight ensures AI systems remain aligned with human values.",
                        "AI systems should implement bias detection and fairness metrics.",
                        "Ethical AI requires transparency, accountability, and respect for human autonomy.",
                    ]
                ),
            }
            for _ in range(random.randint(2, 5))  # 2-5 training samples
        ]

        return {
            "model_name": model_name,
            "model_id": f"load-test-{uuid.uuid4()}",
            "training_data": training_data,
            "lora_config": {
                "r": 16,
                "lora_alpha": 32,
                "target_modules": ["q_proj", "v_proj"],
                "lora_dropout": 0.1,
            },
            "privacy_config": {
                "enable_differential_privacy": True,
                "epsilon": 8.0,
                "delta": 1e-5,
            },
        }

    def _generate_policy_request(self) -> Dict[str, Any]:
        """Generate a policy evaluation request."""
        return {
            "action": "constitutional_training",
            "agent_id": f"load-test-agent-{random.randint(1000, 9999)}",
            "resource": {
                "type": "training_session",
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "context": {
                "user_permissions": ["model_training"],
                "compliance_threshold": 0.95,
            },
        }

    def _check_training_status(self, training_id: str):
        """Check the status of a submitted training job."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        with self.client.get(
            f"/api/v1/train/{training_id}/status",
            headers=headers,
            catch_response=True,
            name="check_training_status",
        ) as response:

            if response.status_code == 200:
                try:
                    status_data = response.json()
                    valid_statuses = ["initializing", "running", "completed", "failed"]
                    if status_data.get("status") not in valid_statuses:
                        response.failure("Invalid training status")
                except json.JSONDecodeError:
                    response.failure("Invalid status response")
            else:
                response.failure(f"Status check failed: {response.status_code}")

    def _record_success(self, name: str, response_time: float):
        """Record a successful request."""
        events.request.fire(
            request_type="GET",
            name=name,
            response_time=response_time,
            response_length=0,
            exception=None,
            context={},
        )

    def _record_failure(self, name: str, error_message: str):
        """Record a failed request."""
        events.request.fire(
            request_type="GET",
            name=name,
            response_time=0,
            response_length=0,
            exception=Exception(error_message),
            context={},
        )


class BaselineLoadUser(ConstitutionalTrainerUser):
    """User class for baseline load testing (10 concurrent users)."""

    weight = 1
    wait_time = between(2, 4)  # Slightly longer wait for baseline


class PeakLoadUser(ConstitutionalTrainerUser):
    """User class for peak load testing (100 concurrent users)."""

    weight = 3
    wait_time = between(1, 2)  # Shorter wait for peak load


# Event handlers for custom metrics and monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test environment and logging."""
    print("🚀 Starting Constitutional Trainer Load Test")
    print(f"Target host: {environment.host}")
    print(
        f"Policy Engine URL: {os.getenv('POLICY_ENGINE_URL', 'http://policy-engine:8001')}"
    )

    # Verify service accessibility
    try:
        response = requests.get(f"{environment.host}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Constitutional Trainer service is accessible")
        else:
            print(
                f"⚠️ Constitutional Trainer health check returned: {response.status_code}"
            )
    except requests.RequestException as e:
        print(f"❌ Cannot reach Constitutional Trainer service: {e}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Clean up and generate final report."""
    print("🏁 Load test completed")
    print("📊 Check Locust web UI for detailed performance metrics")

    # Generate summary report
    stats = environment.stats
    print(f"\n📈 Performance Summary:")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"99th percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Requests per second: {stats.total.current_rps:.2f}")


@events.request.add_listener
def on_request(
    request_type, name, response_time, response_length, exception, context, **kwargs
):
    """Monitor individual requests for performance analysis."""
    if exception:
        print(f"❌ Request failed: {name} - {exception}")
    elif response_time > 5000:  # Log slow requests
        print(f"🐌 Slow request detected: {name} - {response_time:.2f}ms")


# Custom load test shapes for specific scenarios
class BaselineLoadShape:
    """Load shape for baseline testing: ramp to 10 users, sustain, ramp down."""

    def tick(self):
        run_time = self.get_run_time()

        if run_time < 120:  # 0-2 minutes: ramp up to 10 users
            return (round(run_time / 12), 1)
        elif run_time < 420:  # 2-7 minutes: sustain 10 users
            return (10, 1)
        elif run_time < 480:  # 7-8 minutes: ramp down
            return (round((480 - run_time) / 6), 1)
        else:
            return None


class PeakLoadShape:
    """Load shape for peak testing: ramp to 100 users over 5 minutes, sustain."""

    def tick(self):
        run_time = self.get_run_time()

        if run_time < 300:  # 0-5 minutes: ramp up to 100 users
            return (round(run_time / 3), 2)
        elif run_time < 600:  # 5-10 minutes: sustain 100 users
            return (100, 2)
        elif run_time < 720:  # 10-12 minutes: ramp down
            return (round((720 - run_time) / 6), 2)
        else:
            return None


# Configuration for different test scenarios
if __name__ == "__main__":
    # This allows running the script directly for testing
    import subprocess
    import sys

    print("Constitutional Trainer Load Testing Script")
    print("Use 'locust -f constitutional_trainer_locust.py --host=<URL>' to run")

    # Example commands
    print("\nExample commands:")
    print("# Baseline test (10 users)")
    print(
        "locust -f constitutional_trainer_locust.py --host=http://localhost:8000 --users 10 --spawn-rate 1 --run-time 8m"
    )

    print("\n# Peak test (100 users)")
    print(
        "locust -f constitutional_trainer_locust.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 12m"
    )

    print("\n# Spike test (200 users)")
    print(
        "locust -f constitutional_trainer_locust.py --host=http://localhost:8000 --users 200 --spawn-rate 20 --run-time 5m"
    )
