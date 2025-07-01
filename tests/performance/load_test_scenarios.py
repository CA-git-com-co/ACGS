#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Load Testing Scenarios
Phase 2 - Load Testing Configuration and Test Scenarios

This module implements realistic load testing scenarios for the ACGS-1 system
targeting >1000 concurrent users with <500ms response times and >99.9% availability.

Test Scenarios:
1. Basic Health Check Load Test
2. Authentication Flow Load Test
3. Constitutional Governance Workflow Load Test
4. Policy Synthesis Load Test
5. Cross-Service Integration Load Test
6. Blockchain Transaction Load Test

Performance Targets:
- >1000 concurrent users
- <500ms response times for 95% of requests
- >99.9% availability
- <0.01 SOL costs per governance action
"""

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from locust import HttpUser, between, task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestScenario:
    """Configuration for a specific load test scenario."""

    name: str
    description: str
    target_users: int
    spawn_rate: int
    duration_seconds: int
    endpoints: list[dict[str, Any]]
    test_data: dict[str, Any] = field(default_factory=dict)
    success_criteria: dict[str, float] = field(default_factory=dict)


class ACGSHealthCheckUser(HttpUser):
    """Basic health check load testing user."""

    wait_time = between(1, 3)

    def on_start(self):
        """Initialize user session."""
        self.services = [
            ("auth", 8000),
            ("ac", 8001),
            ("integrity", 8002),
            ("fv", 8003),
            ("gs", 8004),
            ("pgc", 8005),
            ("ec", 8006),
        ]

    @task(10)
    def health_check_all_services(self):
        """Test health endpoints for all services."""
        for service_name, port in self.services:
            with self.client.get(
                f"http://localhost:{port}/health",
                catch_response=True,
                name=f"{service_name}_health",
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Health check failed for {service_name}")


class ACGSAuthenticationUser(HttpUser):
    """Authentication flow load testing user."""

    wait_time = between(2, 5)

    def on_start(self):
        """Initialize authentication session."""
        self.auth_token = None
        self.user_id = f"test_user_{random.randint(1000, 9999)}"

    @task(5)
    def login_flow(self):
        """Test complete login flow."""
        # Simulate login
        login_data = {"username": self.user_id, "password": "test_password_123"}

        with self.client.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            catch_response=True,
            name="auth_login",
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    response.success()
                except:
                    response.failure("Invalid login response format")
            else:
                response.failure(f"Login failed: {response.status_code}")

    @task(3)
    def validate_token(self):
        """Test token validation."""
        if self.auth_token:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            with self.client.get(
                "http://localhost:8000/api/v1/auth/validate",
                headers=headers,
                catch_response=True,
                name="auth_validate",
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure("Token validation failed")


class ACGSGovernanceWorkflowUser(HttpUser):
    """Constitutional governance workflow load testing user."""

    wait_time = between(3, 8)

    def on_start(self):
        """Initialize governance session."""
        self.policy_id = None
        self.constitutional_hash = "cdd01ef066bc6cf2"

    @task(8)
    def policy_creation_workflow(self):
        """Test complete policy creation workflow."""
        # Step 1: Create policy draft
        policy_data = {
            "title": f"Test Policy {random.randint(1000, 9999)}",
            "description": "Automated load test policy for constitutional governance",
            "content": "This is a test policy for load testing purposes",
            "constitutional_hash": self.constitutional_hash,
            "priority": random.choice(["low", "medium", "high"]),
        }

        with self.client.post(
            "http://localhost:8005/api/v1/governance/policies",
            json=policy_data,
            catch_response=True,
            name="policy_creation",
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.policy_id = data.get("policy_id")
                    response.success()
                except:
                    response.failure("Invalid policy creation response")
            else:
                response.failure(f"Policy creation failed: {response.status_code}")

    @task(5)
    def constitutional_compliance_check(self):
        """Test constitutional compliance validation."""
        if self.policy_id:
            compliance_data = {
                "policy_id": self.policy_id,
                "constitutional_hash": self.constitutional_hash,
                "validation_level": "standard",
            }

            with self.client.post(
                "http://localhost:8005/api/v1/governance/compliance/validate",
                json=compliance_data,
                catch_response=True,
                name="compliance_check",
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure("Compliance check failed")

    @task(3)
    def policy_enforcement_check(self):
        """Test policy enforcement mechanisms."""
        enforcement_data = {
            "action": "test_governance_action",
            "context": {"test": True, "load_test": True},
            "constitutional_hash": self.constitutional_hash,
        }

        with self.client.post(
            "http://localhost:8005/api/v1/governance/enforcement/check",
            json=enforcement_data,
            catch_response=True,
            name="enforcement_check",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Enforcement check failed")


class ACGSPolicySynthesisUser(HttpUser):
    """Policy synthesis load testing user."""

    wait_time = between(5, 10)

    @task(6)
    def policy_synthesis_request(self):
        """Test policy synthesis engine."""
        synthesis_data = {
            "requirements": "Create a policy for load testing governance systems",
            "context": {
                "domain": "constitutional_governance",
                "complexity": "medium",
                "stakeholders": ["developers", "administrators"],
            },
            "constitutional_hash": "cdd01ef066bc6cf2",
            "synthesis_strategy": "standard",
        }

        with self.client.post(
            "http://localhost:8004/api/v1/synthesis/generate",
            json=synthesis_data,
            catch_response=True,
            name="policy_synthesis",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Policy synthesis failed")

    @task(4)
    def multi_model_consensus(self):
        """Test multi-model consensus engine."""
        consensus_data = {
            "policy_content": "Test policy for multi-model validation",
            "models": ["primary", "secondary"],
            "consensus_threshold": 0.7,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        with self.client.post(
            "http://localhost:8004/api/v1/synthesis/consensus",
            json=consensus_data,
            catch_response=True,
            name="multi_model_consensus",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Multi-model consensus failed")


# Load test scenario configurations
LOAD_TEST_SCENARIOS = {
    "health_check": LoadTestScenario(
        name="Health Check Load Test",
        description="Basic health endpoint load testing across all services",
        target_users=100,
        spawn_rate=10,
        duration_seconds=300,
        endpoints=[
            {"service": "auth", "port": 8000, "path": "/health"},
            {"service": "ac", "port": 8001, "path": "/health"},
            {"service": "integrity", "port": 8002, "path": "/health"},
            {"service": "fv", "port": 8003, "path": "/health"},
            {"service": "gs", "port": 8004, "path": "/health"},
            {"service": "pgc", "port": 8005, "path": "/health"},
            {"service": "ec", "port": 8006, "path": "/health"},
        ],
        success_criteria={
            "response_time_95th_percentile": 500.0,  # ms
            "success_rate": 99.9,  # %
            "error_rate": 0.1,  # %
        },
    ),
    "authentication_flow": LoadTestScenario(
        name="Authentication Flow Load Test",
        description="Complete authentication workflow load testing",
        target_users=200,
        spawn_rate=20,
        duration_seconds=600,
        endpoints=[
            {"service": "auth", "port": 8000, "path": "/api/v1/auth/login"},
            {"service": "auth", "port": 8000, "path": "/api/v1/auth/validate"},
        ],
        success_criteria={
            "response_time_95th_percentile": 1000.0,
            "success_rate": 99.5,
            "error_rate": 0.5,
        },
    ),
    "governance_workflow": LoadTestScenario(
        name="Constitutional Governance Workflow Load Test",
        description="End-to-end governance workflow load testing",
        target_users=500,
        spawn_rate=25,
        duration_seconds=900,
        endpoints=[
            {"service": "pgc", "port": 8005, "path": "/api/v1/governance/policies"},
            {
                "service": "pgc",
                "port": 8005,
                "path": "/api/v1/governance/compliance/validate",
            },
            {
                "service": "pgc",
                "port": 8005,
                "path": "/api/v1/governance/enforcement/check",
            },
        ],
        success_criteria={
            "response_time_95th_percentile": 2000.0,
            "success_rate": 99.0,
            "error_rate": 1.0,
        },
    ),
    "policy_synthesis": LoadTestScenario(
        name="Policy Synthesis Load Test",
        description="Policy synthesis engine load testing",
        target_users=300,
        spawn_rate=15,
        duration_seconds=1200,
        endpoints=[
            {"service": "gs", "port": 8004, "path": "/api/v1/synthesis/generate"},
            {"service": "gs", "port": 8004, "path": "/api/v1/synthesis/consensus"},
        ],
        success_criteria={
            "response_time_95th_percentile": 5000.0,
            "success_rate": 98.0,
            "error_rate": 2.0,
        },
    ),
    "full_system": LoadTestScenario(
        name="Full System Load Test",
        description="Comprehensive system load test with >1000 concurrent users",
        target_users=1000,
        spawn_rate=50,
        duration_seconds=1800,  # 30 minutes
        endpoints=[],  # All endpoints
        success_criteria={
            "response_time_95th_percentile": 500.0,
            "success_rate": 99.9,
            "error_rate": 0.1,
            "concurrent_users": 1000.0,
        },
    ),
}


def create_load_test_report(
    scenario_name: str, stats: dict[str, Any]
) -> dict[str, Any]:
    """Create comprehensive load test report."""
    scenario = LOAD_TEST_SCENARIOS.get(scenario_name, {})

    report = {
        "scenario": scenario_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "target_users": getattr(scenario, "target_users", 0),
            "duration_seconds": getattr(scenario, "duration_seconds", 0),
            "spawn_rate": getattr(scenario, "spawn_rate", 0),
        },
        "results": stats,
        "success_criteria": getattr(scenario, "success_criteria", {}),
        "status": "completed",
    }

    # Evaluate success criteria
    criteria_met = True
    if hasattr(scenario, "success_criteria"):
        for criterion, target in scenario.success_criteria.items():
            actual = stats.get(criterion, 0)
            if (criterion.endswith("_rate") and actual < target) or (
                criterion.endswith("_percentile") and actual > target
            ):
                criteria_met = False

    report["criteria_met"] = criteria_met
    report["overall_status"] = "PASS" if criteria_met else "FAIL"

    return report


if __name__ == "__main__":
    print("ACGS-1 Load Testing Scenarios Configuration")
    print("=" * 50)

    for scenario_name, scenario in LOAD_TEST_SCENARIOS.items():
        print(f"\n{scenario.name}")
        print(f"Description: {scenario.description}")
        print(f"Target Users: {scenario.target_users}")
        print(f"Duration: {scenario.duration_seconds}s")
        print(f"Success Criteria: {scenario.success_criteria}")
