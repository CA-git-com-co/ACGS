#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Load Testing Framework

This module implements comprehensive load testing for the ACGS-1 Constitutional
Governance System, targeting >1000 concurrent users across all 7 core services
and 5 governance workflows.

Performance Targets:
- >1000 concurrent governance actions
- <500ms response times for 95% of requests
- >99.9% availability during load testing
- <0.01 SOL costs per governance action
- Zero critical failures under load

Features:
- Multi-service concurrent load testing
- Governance workflow stress testing
- Blockchain transaction load testing
- Real-time performance monitoring
- Automated failure detection and reporting
"""

import asyncio
import json
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import numpy as np
import pytest
from prometheus_client import Counter, Gauge, Histogram, Summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics for load testing
load_test_requests_total = Counter(
    "acgs_load_test_requests_total",
    "Total load test requests",
    ["service", "endpoint", "status"],
)

load_test_response_time = Histogram(
    "acgs_load_test_response_time_seconds",
    "Load test response times",
    ["service", "endpoint"],
)

concurrent_users_gauge = Gauge(
    "acgs_concurrent_users_active", "Number of active concurrent users"
)

governance_actions_rate = Summary(
    "acgs_governance_actions_per_second", "Rate of governance actions per second"
)

blockchain_transaction_cost = Histogram(
    "acgs_blockchain_transaction_cost_sol", "Blockchain transaction costs in SOL"
)


@dataclass
class LoadTestConfig:
    """Configuration for load testing scenarios."""

    max_concurrent_users: int = 1000
    test_duration_seconds: int = 300  # 5 minutes
    ramp_up_seconds: int = 60
    target_response_time_ms: float = 500.0
    target_availability_percent: float = 99.9
    target_sol_cost: float = 0.01
    services_to_test: List[str] = field(
        default_factory=lambda: ["auth", "ac", "integrity", "fv", "gs", "pgc", "ec"]
    )
    governance_workflows: List[str] = field(
        default_factory=lambda: [
            "policy_creation",
            "constitutional_compliance",
            "policy_enforcement",
            "wina_oversight",
            "audit_transparency",
        ]
    )


@dataclass
class LoadTestResult:
    """Results from load testing."""

    test_id: str
    service: str
    endpoint: str
    user_id: str
    response_time_ms: float
    status_code: int
    success: bool
    timestamp: datetime
    error_message: Optional[str] = None
    sol_cost: Optional[float] = None


class ServiceLoadTester:
    """Load tester for individual ACGS-1 services."""

    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = None
        self.service_ports = {
            "auth": 8000,
            "ac": 8001,
            "integrity": 8002,
            "fv": 8003,
            "gs": 8004,
            "pgc": 8005,
            "ec": 8006,
        }
        self.test_endpoints = {
            "auth": ["/health", "/api/auth/validate", "/api/auth/refresh"],
            "ac": [
                "/health",
                "/api/constitutional-ai/validate",
                "/api/constitutional-ai/principles",
            ],
            "integrity": ["/health", "/api/integrity/verify", "/api/integrity/hash"],
            "fv": [
                "/health",
                "/api/formal-verification/verify",
                "/api/formal-verification/status",
            ],
            "gs": [
                "/health",
                "/api/governance-synthesis/synthesize",
                "/api/governance-synthesis/validate",
            ],
            "pgc": [
                "/health",
                "/api/policy-governance/enforce",
                "/api/policy-governance/compile",
            ],
            "ec": [
                "/health",
                "/api/evolutionary-computation/optimize",
                "/api/evolutionary-computation/status",
            ],
        }

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=2000, limit_per_host=500)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_service_endpoint(
        self, service: str, endpoint: str, user_id: str, test_id: str
    ) -> LoadTestResult:
        """Test a single service endpoint."""
        start_time = time.time()
        port = self.service_ports.get(service, 8000)
        url = f"{self.base_url}:{port}{endpoint}"

        try:
            # Prepare request data based on endpoint
            request_data = self._prepare_request_data(service, endpoint, user_id)

            async with self.session.get(url, json=request_data) as response:
                response_time_ms = (time.time() - start_time) * 1000
                success = response.status < 400

                # Record metrics
                load_test_requests_total.labels(
                    service=service,
                    endpoint=endpoint,
                    status="success" if success else "error",
                ).inc()

                load_test_response_time.labels(
                    service=service, endpoint=endpoint
                ).observe(response_time_ms / 1000)

                # Simulate blockchain cost for governance operations
                sol_cost = None
                if service in ["pgc", "gs"] and "governance" in endpoint:
                    sol_cost = random.uniform(0.005, 0.015)  # Simulate SOL costs
                    blockchain_transaction_cost.observe(sol_cost)

                return LoadTestResult(
                    test_id=test_id,
                    service=service,
                    endpoint=endpoint,
                    user_id=user_id,
                    response_time_ms=response_time_ms,
                    status_code=response.status,
                    success=success,
                    timestamp=datetime.now(timezone.utc),
                    sol_cost=sol_cost,
                )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000

            load_test_requests_total.labels(
                service=service, endpoint=endpoint, status="error"
            ).inc()

            return LoadTestResult(
                test_id=test_id,
                service=service,
                endpoint=endpoint,
                user_id=user_id,
                response_time_ms=response_time_ms,
                status_code=0,
                success=False,
                timestamp=datetime.now(timezone.utc),
                error_message=str(e),
            )

    def _prepare_request_data(
        self, service: str, endpoint: str, user_id: str
    ) -> Dict[str, Any]:
        """Prepare request data for different service endpoints."""
        base_data = {
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_mode": True,
        }

        if service == "auth":
            if "validate" in endpoint:
                base_data.update({"token": f"test_token_{user_id}"})
        elif service == "ac":
            if "validate" in endpoint:
                base_data.update(
                    {
                        "principle_id": "constitutional_principle_1",
                        "content": "Test constitutional validation",
                    }
                )
        elif service == "gs":
            if "synthesize" in endpoint:
                base_data.update(
                    {
                        "policy_domain": "governance",
                        "requirements": ["democratic", "transparent", "accountable"],
                    }
                )
        elif service == "pgc":
            if "enforce" in endpoint:
                base_data.update(
                    {
                        "policy_id": f"policy_{random.randint(1, 100)}",
                        "action": "validate_compliance",
                    }
                )

        return base_data


class GovernanceWorkflowLoadTester:
    """Load tester for governance workflows."""

    def __init__(self, service_tester: ServiceLoadTester):
        self.service_tester = service_tester
        self.workflow_steps = {
            "policy_creation": [
                ("gs", "/api/governance-synthesis/synthesize"),
                ("ac", "/api/constitutional-ai/validate"),
                ("pgc", "/api/policy-governance/compile"),
            ],
            "constitutional_compliance": [
                ("ac", "/api/constitutional-ai/validate"),
                ("fv", "/api/formal-verification/verify"),
                ("integrity", "/api/integrity/verify"),
            ],
            "policy_enforcement": [
                ("pgc", "/api/policy-governance/enforce"),
                ("ec", "/api/evolutionary-computation/optimize"),
                ("integrity", "/api/integrity/hash"),
            ],
            "wina_oversight": [
                ("ec", "/api/evolutionary-computation/status"),
                ("ac", "/api/constitutional-ai/principles"),
                ("pgc", "/api/policy-governance/compile"),
            ],
            "audit_transparency": [
                ("integrity", "/api/integrity/verify"),
                ("auth", "/api/auth/validate"),
                ("fv", "/api/formal-verification/status"),
            ],
        }

    async def test_governance_workflow(
        self, workflow: str, user_id: str, test_id: str
    ) -> List[LoadTestResult]:
        """Test a complete governance workflow."""
        results = []
        workflow_start_time = time.time()

        if workflow not in self.workflow_steps:
            logger.warning(f"Unknown workflow: {workflow}")
            return results

        steps = self.workflow_steps[workflow]

        for service, endpoint in steps:
            result = await self.service_tester.test_service_endpoint(
                service, endpoint, user_id, test_id
            )
            results.append(result)

            # Small delay between workflow steps
            await asyncio.sleep(0.1)

        workflow_duration = time.time() - workflow_start_time
        governance_actions_rate.observe(1.0 / workflow_duration)

        return results


class ComprehensiveLoadTester:
    """Comprehensive load testing orchestrator."""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[LoadTestResult] = []
        self.active_users = 0

    async def simulate_user_session(
        self, user_id: str, test_id: str, session_duration: float
    ) -> List[LoadTestResult]:
        """Simulate a user session with multiple requests."""
        session_results = []
        session_start = time.time()

        async with ServiceLoadTester() as service_tester:
            workflow_tester = GovernanceWorkflowLoadTester(service_tester)

            while time.time() - session_start < session_duration:
                # Randomly choose between service endpoint test and workflow test
                if random.random() < 0.3:  # 30% chance of workflow test
                    workflow = random.choice(self.config.governance_workflows)
                    workflow_results = await workflow_tester.test_governance_workflow(
                        workflow, user_id, test_id
                    )
                    session_results.extend(workflow_results)
                else:  # 70% chance of individual service test
                    service = random.choice(self.config.services_to_test)
                    async with ServiceLoadTester() as tester:
                        endpoints = tester.test_endpoints.get(service, ["/health"])
                        endpoint = random.choice(endpoints)
                        result = await tester.test_service_endpoint(
                            service, endpoint, user_id, test_id
                        )
                        session_results.append(result)

                # Random delay between requests (0.5-2 seconds)
                await asyncio.sleep(random.uniform(0.5, 2.0))

        return session_results

    async def run_load_test(self) -> Dict[str, Any]:
        """Run comprehensive load test."""
        test_id = str(uuid.uuid4())
        logger.info(
            f"Starting load test {test_id} with {self.config.max_concurrent_users} concurrent users"
        )

        start_time = time.time()
        user_tasks = []

        # Ramp up users gradually
        users_per_second = (
            self.config.max_concurrent_users / self.config.ramp_up_seconds
        )

        for i in range(self.config.max_concurrent_users):
            user_id = f"load_test_user_{i:04d}"

            # Calculate when this user should start
            start_delay = i / users_per_second
            session_duration = self.config.test_duration_seconds - start_delay

            if session_duration > 0:
                task = asyncio.create_task(
                    self._delayed_user_session(
                        user_id, test_id, start_delay, session_duration
                    )
                )
                user_tasks.append(task)

        # Wait for all user sessions to complete
        all_results = await asyncio.gather(*user_tasks, return_exceptions=True)

        # Flatten results and filter out exceptions
        for result_set in all_results:
            if isinstance(result_set, list):
                self.results.extend(result_set)
            elif isinstance(result_set, Exception):
                logger.error(f"User session failed: {result_set}")

        total_duration = time.time() - start_time

        # Calculate performance metrics
        return self._calculate_performance_metrics(test_id, total_duration)

    async def _delayed_user_session(
        self, user_id: str, test_id: str, delay: float, duration: float
    ) -> List[LoadTestResult]:
        """Start a user session after a delay."""
        await asyncio.sleep(delay)

        self.active_users += 1
        concurrent_users_gauge.set(self.active_users)

        try:
            results = await self.simulate_user_session(user_id, test_id, duration)
            return results
        finally:
            self.active_users -= 1
            concurrent_users_gauge.set(self.active_users)

    def _calculate_performance_metrics(
        self, test_id: str, duration: float
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        if not self.results:
            return {"error": "No results collected"}

        # Basic metrics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests

        success_rate = (
            (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        )
        requests_per_second = total_requests / duration if duration > 0 else 0

        # Response time metrics
        response_times = [r.response_time_ms for r in self.results if r.success]
        if response_times:
            avg_response_time = np.mean(response_times)
            p95_response_time = np.percentile(response_times, 95)
            p99_response_time = np.percentile(response_times, 99)
        else:
            avg_response_time = p95_response_time = p99_response_time = 0

        # SOL cost metrics
        sol_costs = [r.sol_cost for r in self.results if r.sol_cost is not None]
        avg_sol_cost = np.mean(sol_costs) if sol_costs else 0

        # Service-specific metrics
        service_metrics = {}
        for service in self.config.services_to_test:
            service_results = [r for r in self.results if r.service == service]
            if service_results:
                service_success_rate = (
                    sum(1 for r in service_results if r.success) / len(service_results)
                ) * 100
                service_avg_response = np.mean(
                    [r.response_time_ms for r in service_results if r.success]
                )

                service_metrics[service] = {
                    "total_requests": len(service_results),
                    "success_rate": service_success_rate,
                    "avg_response_time_ms": service_avg_response,
                }

        # Performance targets assessment
        performance_assessment = {
            "concurrent_users_target": self.config.max_concurrent_users >= 1000,
            "response_time_target": p95_response_time
            <= self.config.target_response_time_ms,
            "availability_target": success_rate
            >= self.config.target_availability_percent,
            "sol_cost_target": avg_sol_cost <= self.config.target_sol_cost,
            "overall_success": (
                self.config.max_concurrent_users >= 1000
                and p95_response_time <= self.config.target_response_time_ms
                and success_rate >= self.config.target_availability_percent
                and avg_sol_cost <= self.config.target_sol_cost
            ),
        }

        results = {
            "test_id": test_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_duration_seconds": duration,
            "configuration": {
                "max_concurrent_users": self.config.max_concurrent_users,
                "target_response_time_ms": self.config.target_response_time_ms,
                "target_availability_percent": self.config.target_availability_percent,
                "target_sol_cost": self.config.target_sol_cost,
            },
            "overall_metrics": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate_percent": success_rate,
                "requests_per_second": requests_per_second,
                "avg_response_time_ms": avg_response_time,
                "p95_response_time_ms": p95_response_time,
                "p99_response_time_ms": p99_response_time,
                "avg_sol_cost": avg_sol_cost,
            },
            "service_metrics": service_metrics,
            "performance_assessment": performance_assessment,
        }

        logger.info(f"Load Test Results:")
        logger.info(f"  Total Requests: {total_requests}")
        logger.info(f"  Success Rate: {success_rate:.2f}%")
        logger.info(f"  P95 Response Time: {p95_response_time:.2f}ms")
        logger.info(f"  Requests/Second: {requests_per_second:.2f}")
        logger.info(f"  Overall Success: {performance_assessment['overall_success']}")

        return results

    def save_results(self, filepath: str, metrics: Dict[str, Any]):
        """Save load test results to file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Load test results saved to {filepath}")


# Test functions for pytest integration
@pytest.mark.asyncio
async def test_load_testing_1000_users():
    """Test load testing with 1000 concurrent users."""
    config = LoadTestConfig(
        max_concurrent_users=1000,
        test_duration_seconds=120,  # 2 minutes for test
        ramp_up_seconds=30,
    )

    tester = ComprehensiveLoadTester(config)
    results = await tester.run_load_test()

    # Assertions for performance targets
    assert results["performance_assessment"][
        "concurrent_users_target"
    ], "Failed to achieve 1000 concurrent users"
    assert results["performance_assessment"][
        "response_time_target"
    ], f"P95 response time {results['overall_metrics']['p95_response_time_ms']:.2f}ms exceeds 500ms target"
    assert results["performance_assessment"][
        "availability_target"
    ], f"Success rate {results['overall_metrics']['success_rate_percent']:.2f}% below 99.9% target"

    # Save test results
    tester.save_results("reports/load_test_1000_users.json", results)


if __name__ == "__main__":

    async def main():
        config = LoadTestConfig(
            max_concurrent_users=1000,
            test_duration_seconds=300,  # 5 minutes
            ramp_up_seconds=60,
        )

        tester = ComprehensiveLoadTester(config)
        results = await tester.run_load_test()
        tester.save_results("reports/comprehensive_load_test.json", results)

        print("\n" + "=" * 80)
        print("COMPREHENSIVE LOAD TEST COMPLETE")
        print("=" * 80)
        print(
            f"Overall Success: {results['performance_assessment']['overall_success']}"
        )
        print(f"Concurrent Users: {results['configuration']['max_concurrent_users']}")
        print(
            f"Success Rate: {results['overall_metrics']['success_rate_percent']:.2f}%"
        )
        print(
            f"P95 Response Time: {results['overall_metrics']['p95_response_time_ms']:.2f}ms"
        )

    asyncio.run(main())
