"""
ACGS Enterprise Load Testing Suite

Comprehensive load testing for ACGS constitutional AI system
targeting ≥1,000 RPS with constitutional compliance validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import random
from datetime import datetime, timezone
from typing import Any

from locust import HttpUser, between, events, task
from locust.runners import MasterRunner, WorkerRunner

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Test configuration
class LoadTestConfig:
    """Load test configuration settings."""

    # Target performance metrics
    TARGET_RPS = 1000
    MAX_RESPONSE_TIME_MS = 2000
    ERROR_RATE_THRESHOLD = 0.01  # 1%

    # Constitutional compliance requirements
    CONSTITUTIONAL_COMPLIANCE_REQUIRED = True
    MIN_COMPLIANCE_SCORE = 0.95

    # Test data
    TENANT_COUNT = 50
    USERS_PER_TENANT = 20

    # Load test scenarios
    SCENARIOS = {
        "constitutional_verification": 0.25,  # 25% of requests
        "multi_tenant_operations": 0.30,  # 30% of requests
        "policy_governance": 0.20,  # 20% of requests
        "formal_verification": 0.15,  # 15% of requests
        "integrity_operations": 0.10,  # 10% of requests
    }


# Test data generators
class TestDataGenerator:
    """Generate test data for load testing."""

    def __init__(self):
        self.tenant_ids = [
            f"tenant-{i:04d}" for i in range(1, LoadTestConfig.TENANT_COUNT + 1)
        ]
        self.user_ids = [
            f"user-{i:06d}"
            for i in range(
                1, LoadTestConfig.TENANT_COUNT * LoadTestConfig.USERS_PER_TENANT + 1
            )
        ]
        self.policy_templates = [
            "authentication_policy",
            "data_access_policy",
            "multi_tenant_isolation_policy",
            "constitutional_governance_policy",
            "formal_verification_policy",
        ]

    def get_random_tenant(self) -> str:
        """Get random tenant ID."""
        return random.choice(self.tenant_ids)

    def get_random_user(self, tenant_id: str = None) -> str:
        """Get random user ID, optionally for specific tenant."""
        if tenant_id:
            # Calculate users for specific tenant
            tenant_index = self.tenant_ids.index(tenant_id)
            start_user = tenant_index * LoadTestConfig.USERS_PER_TENANT
            end_user = start_user + LoadTestConfig.USERS_PER_TENANT
            return f"user-{random.randint(start_user + 1, end_user):06d}"
        return random.choice(self.user_ids)

    def get_random_policy_template(self) -> str:
        """Get random policy template."""
        return random.choice(self.policy_templates)

    def generate_policy_content(self) -> dict[str, Any]:
        """Generate sample policy content."""
        return {
            "rule": f"test_rule_{random.randint(1000, 9999)}",
            "constraints": [
                "constitutional_compliance_required",
                "multi_tenant_isolation_enforced",
                "audit_trail_maintained",
            ],
            "conditions": {
                "user_authenticated": True,
                "tenant_verified": True,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "load_test": True,
            },
        }

    def generate_verification_request(self) -> dict[str, Any]:
        """Generate formal verification request."""
        return {
            "policy_content": self.generate_policy_content(),
            "verification_type": "constitutional_compliance",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "tenant_id": self.get_random_tenant(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global test data generator
test_data = TestDataGenerator()


class ACGSLoadTestUser(HttpUser):
    """
    ACGS Load Test User simulating enterprise workloads.

    Simulates realistic user behavior with constitutional compliance
    requirements and multi-tenant operations.
    """

    wait_time = between(0.1, 2.0)  # 100ms to 2s between requests

    def on_start(self):
        """Initialize user session."""
        self.tenant_id = test_data.get_random_tenant()
        self.user_id = test_data.get_random_user(self.tenant_id)
        self.auth_token = None
        self.constitutional_compliance_score = 0.0

        # Authenticate user
        self.authenticate()

        logger.info(
            f"Load test user started: {self.user_id} (tenant: {self.tenant_id})"
        )

    def authenticate(self):
        """Authenticate user and get JWT token."""
        auth_data = {
            "username": self.user_id,
            "tenant_id": self.tenant_id,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        with self.client.post(
            "/api/auth/login",
            json=auth_data,
            headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
            catch_response=True,
            name="auth_login",
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    response.success()
                except:
                    response.failure("Failed to parse auth response")
            else:
                response.failure(f"Auth failed: {response.status_code}")

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        headers = {
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            "X-Tenant-ID": self.tenant_id,
            "X-User-ID": self.user_id,
        }

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        return headers

    @task(25)  # 25% weight
    def constitutional_verification_scenario(self):
        """Test constitutional compliance verification."""

        # Test constitutional hash verification
        with self.client.get(
            "/api/constitutional/verify",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="constitutional_verify",
        ) as response:
            self.validate_constitutional_response(response, "constitutional_verify")

        # Test compliance scoring
        compliance_data = {
            "operation": "multi_tenant_data_access",
            "tenant_id": self.tenant_id,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        with self.client.post(
            "/api/constitutional/score",
            json=compliance_data,
            headers=self.get_auth_headers(),
            catch_response=True,
            name="constitutional_score",
        ) as response:
            self.validate_constitutional_response(response, "constitutional_score")

    @task(30)  # 30% weight
    def multi_tenant_operations_scenario(self):
        """Test multi-tenant operations."""

        # Test tenant data access
        with self.client.get(
            f"/api/tenant/{self.tenant_id}/data",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="tenant_data_access",
        ) as response:
            self.validate_constitutional_response(response, "tenant_data_access")

        # Test cross-tenant access prevention
        other_tenant = test_data.get_random_tenant()
        if other_tenant != self.tenant_id:
            with self.client.get(
                f"/api/tenant/{other_tenant}/data",
                headers=self.get_auth_headers(),
                catch_response=True,
                name="cross_tenant_access_attempt",
            ) as response:
                # This should fail with 403
                if response.status_code == 403:
                    response.success()
                else:
                    response.failure(
                        "Cross-tenant access should be forbidden, got"
                        f" {response.status_code}"
                    )

        # Test tenant configuration
        config_data = {
            "setting": "constitutional_compliance_level",
            "value": "strict",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        with self.client.put(
            f"/api/tenant/{self.tenant_id}/config",
            json=config_data,
            headers=self.get_auth_headers(),
            catch_response=True,
            name="tenant_config_update",
        ) as response:
            self.validate_constitutional_response(response, "tenant_config_update")

    @task(20)  # 20% weight
    def policy_governance_scenario(self):
        """Test policy governance operations."""

        # Create policy
        policy_data = test_data.generate_policy_content()

        with self.client.post(
            "/api/policy/create",
            json=policy_data,
            headers=self.get_auth_headers(),
            catch_response=True,
            name="policy_create",
        ) as response:
            self.validate_constitutional_response(response, "policy_create")

            if response.status_code == 201:
                try:
                    created_policy = response.json()
                    policy_id = created_policy.get("policy_id")

                    # Test policy retrieval
                    if policy_id:
                        with self.client.get(
                            f"/api/policy/{policy_id}",
                            headers=self.get_auth_headers(),
                            catch_response=True,
                            name="policy_get",
                        ) as get_response:
                            self.validate_constitutional_response(
                                get_response, "policy_get"
                            )
                except:
                    pass

        # Test policy listing
        with self.client.get(
            "/api/policy/list",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="policy_list",
        ) as response:
            self.validate_constitutional_response(response, "policy_list")

    @task(15)  # 15% weight
    def formal_verification_scenario(self):
        """Test formal verification operations."""

        verification_request = test_data.generate_verification_request()

        with self.client.post(
            "/api/verification/verify",
            json=verification_request,
            headers=self.get_auth_headers(),
            catch_response=True,
            name="formal_verification",
        ) as response:
            self.validate_constitutional_response(response, "formal_verification")

            if response.status_code == 200:
                try:
                    verification_result = response.json()
                    is_compliant = verification_result.get("is_compliant", False)
                    constitutional_hash = verification_result.get("constitutional_hash")

                    if constitutional_hash != CONSTITUTIONAL_HASH:
                        response.failure(
                            "Constitutional hash mismatch in verification response"
                        )
                    elif not is_compliant:
                        response.failure("Verification failed compliance check")
                except:
                    response.failure("Failed to parse verification response")

        # Test verification status
        with self.client.get(
            "/api/verification/status",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="verification_status",
        ) as response:
            self.validate_constitutional_response(response, "verification_status")

    @task(10)  # 10% weight
    def integrity_operations_scenario(self):
        """Test integrity service operations."""

        # Test audit trail verification
        with self.client.get(
            "/api/integrity/audit/verify",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="audit_verify",
        ) as response:
            self.validate_constitutional_response(response, "audit_verify")

        # Create audit event
        audit_event = {
            "event_type": "load_test_operation",
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "details": {
                "operation": "constitutional_compliance_test",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with self.client.post(
            "/api/integrity/audit/create",
            json=audit_event,
            headers=self.get_auth_headers(),
            catch_response=True,
            name="audit_create",
        ) as response:
            self.validate_constitutional_response(response, "audit_create")

        # Test hash chain integrity
        with self.client.get(
            "/api/integrity/chain/verify",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="chain_verify",
        ) as response:
            self.validate_constitutional_response(response, "chain_verify")

    def validate_constitutional_response(self, response, operation_name: str):
        """Validate response for constitutional compliance."""

        # Check basic response
        if response.status_code >= 500:
            response.failure(f"Server error: {response.status_code}")
            return

        if (
            response.status_code >= 400 and response.status_code != 403
        ):  # 403 is expected for cross-tenant
            response.failure(f"Client error: {response.status_code}")
            return

        # Check constitutional compliance if enabled
        if LoadTestConfig.CONSTITUTIONAL_COMPLIANCE_REQUIRED:
            constitutional_hash = response.headers.get("X-Constitutional-Hash")
            if constitutional_hash != CONSTITUTIONAL_HASH:
                response.failure(
                    f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, got"
                    f" {constitutional_hash}"
                )
                return

            # Check compliance score if available
            compliance_score = response.headers.get("X-Constitutional-Score")
            if compliance_score:
                try:
                    score = float(compliance_score)
                    if score < LoadTestConfig.MIN_COMPLIANCE_SCORE:
                        response.failure(
                            f"Constitutional compliance score too low: {score}"
                        )
                        return
                except:
                    pass

        # Check response time
        if (
            response.elapsed.total_seconds() * 1000
            > LoadTestConfig.MAX_RESPONSE_TIME_MS
        ):
            response.failure(
                f"Response time exceeded {LoadTestConfig.MAX_RESPONSE_TIME_MS}ms"
            )
            return

        response.success()


# Load test event handlers
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Handle test start event."""
    logger.info("=== ACGS Enterprise Load Test Started ===")
    logger.info(f"Target RPS: {LoadTestConfig.TARGET_RPS}")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"Max Response Time: {LoadTestConfig.MAX_RESPONSE_TIME_MS}ms")
    logger.info(f"Error Rate Threshold: {LoadTestConfig.ERROR_RATE_THRESHOLD * 100}%")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Handle test stop event."""
    logger.info("=== ACGS Enterprise Load Test Completed ===")


@events.request_success.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """Handle successful requests."""
    # Log constitutional compliance metrics


@events.request_failure.add_listener
def on_request_failure(
    request_type, name, response_time, response_length, exception, **kwargs
):
    """Handle failed requests."""
    logger.warning(f"Request failed: {name} - {exception}")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialize load test environment."""

    # Configure based on runner type
    if isinstance(environment.runner, MasterRunner):
        logger.info("Locust master runner initialized")
    elif isinstance(environment.runner, WorkerRunner):
        logger.info("Locust worker runner initialized")
    else:
        logger.info("Locust standalone runner initialized")

    # Set constitutional compliance requirements
    environment.constitutional_hash = CONSTITUTIONAL_HASH
    environment.compliance_required = LoadTestConfig.CONSTITUTIONAL_COMPLIANCE_REQUIRED


# Performance testing scenarios
class HighVolumeUser(ACGSLoadTestUser):
    """High-volume user for stress testing."""

    wait_time = between(0.05, 0.5)  # Faster requests


class BurstTrafficUser(ACGSLoadTestUser):
    """Burst traffic pattern for spike testing."""

    wait_time = between(0.01, 0.1)  # Very fast bursts


class SustainedLoadUser(ACGSLoadTestUser):
    """Sustained load for endurance testing."""

    wait_time = between(1.0, 3.0)  # Steady, sustained load


# Custom load test shapes
from locust import LoadTestShape


class EnterpriseLoadTestShape(LoadTestShape):
    """
    Enterprise load test shape simulating realistic traffic patterns.

    Gradually ramps up to target RPS and maintains load for testing.
    """

    stages = [
        # Ramp up phase
        {"duration": 60, "users": 50, "spawn_rate": 2},  # 1 min: ramp to 50 users
        {"duration": 120, "users": 200, "spawn_rate": 5},  # 2 min: ramp to 200 users
        {"duration": 300, "users": 500, "spawn_rate": 10},  # 5 min: ramp to 500 users
        {
            "duration": 600,
            "users": 1000,
            "spawn_rate": 15,
        },  # 10 min: ramp to 1000 users
        # Sustained load phase
        {
            "duration": 1200,
            "users": 1000,
            "spawn_rate": 0,
        },  # 20 min: sustain 1000 users
        # Peak load phase
        {
            "duration": 1500,
            "users": 1500,
            "spawn_rate": 20,
        },  # 25 min: peak at 1500 users
        {"duration": 1800, "users": 1500, "spawn_rate": 0},  # 30 min: sustain peak
        # Ramp down phase
        {"duration": 1980, "users": 500, "spawn_rate": -20},  # 33 min: ramp down to 500
        {"duration": 2100, "users": 100, "spawn_rate": -10},  # 35 min: ramp down to 100
        {"duration": 2160, "users": 0, "spawn_rate": -5},  # 36 min: complete
    ]

    def tick(self):
        """Return the load shape for current time."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]

        return None  # End of test


class SpikeTesting(LoadTestShape):
    """Spike testing pattern for sudden load increases."""

    def tick(self):
        run_time = self.get_run_time()

        if run_time < 60:
            return 100, 5  # Normal load
        elif run_time < 120:
            return 2000, 50  # Sudden spike
        elif run_time < 180:
            return 100, -50  # Back to normal
        elif run_time < 240:
            return 100, 0  # Sustained normal
        else:
            return None  # End test


if __name__ == "__main__":
    # Run standalone for testing
    import subprocess
    import sys

    logger.info("Starting ACGS enterprise load test")

    # Default locust command for enterprise testing
    cmd = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        __file__,
        "--host",
        "http://localhost:8080",  # API Gateway
        "--users",
        "1000",
        "--spawn-rate",
        "10",
        "--run-time",
        "30m",
        "--html",
        "acgs_load_test_report.html",
        "--csv",
        "acgs_load_test_results",
    ]

    subprocess.run(cmd)
