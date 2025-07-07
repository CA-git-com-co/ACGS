"""
ACGS E2E Test Utilities

Provides utility classes and functions for test environment management,
data generation, and common testing operations.
"""

import asyncio
import json
import os
import shutil
import tempfile
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import E2ETestConfig, E2ETestMode


@dataclass
class TestEnvironment:
    """Test environment configuration."""

    temp_dir: Path
    database_url: str
    redis_url: str
    config_file: Path


class TestEnvironmentManager:
    """Manages test environment setup and cleanup."""

    def __init__(self, config: E2ETestConfig):
        self.config = config
        self.temp_dir: Optional[Path] = None
        self.test_env: Optional[TestEnvironment] = None
        self.db_engine = None
        self.redis_client: Optional[Redis] = None

    async def setup(self):
        """Setup test environment."""
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="acgs_e2e_"))

        # Setup database if needed
        if self.config.test_mode in [E2ETestMode.ONLINE, E2ETestMode.HYBRID]:
            await self._setup_database()
            await self._setup_redis()

        # Create test environment
        self.test_env = TestEnvironment(
            temp_dir=self.temp_dir,
            database_url=self.config.get_test_database_url(),
            redis_url=self.config.infrastructure.redis_url,
            config_file=self.temp_dir / "test_config.yaml",
        )

        # Write test configuration
        await self._write_test_config()

    async def cleanup(self):
        """Cleanup test environment."""
        if self.db_engine:
            await self.db_engine.dispose()

        if self.redis_client:
            await self.redis_client.aclose()

        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    async def _setup_database(self):
        """Setup test database."""
        if self.config.test_mode == E2ETestMode.OFFLINE:
            return

        # Create database engine
        self.db_engine = create_async_engine(
            self.config.get_test_database_url(), echo=self.config.debug_mode
        )

        # Test connection
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute("SELECT 1")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to test database: {e}")

    async def _setup_redis(self):
        """Setup test Redis connection."""
        if self.config.test_mode == E2ETestMode.OFFLINE:
            return

        self.redis_client = Redis.from_url(
            self.config.infrastructure.redis_url, decode_responses=True
        )

        # Test connection
        try:
            await self.redis_client.ping()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to test Redis: {e}")

    async def _write_test_config(self):
        """Write test configuration to file."""
        config_data = {
            "test_mode": self.config.test_mode,
            "constitutional_hash": self.config.constitutional_hash,
            "services": {
                service_type.value: {
                    "url": endpoint.url,
                    "port": endpoint.port,
                    "health_path": endpoint.health_path,
                }
                for service_type, endpoint in self.config.services.items()
            },
            "infrastructure": {
                "database_url": self.test_env.database_url,
                "redis_url": self.test_env.redis_url,
            },
            "performance_targets": {
                "p99_latency_ms": self.config.performance.p99_latency_ms,
                "cache_hit_rate": self.config.performance.cache_hit_rate,
                "throughput_rps": self.config.performance.throughput_rps,
                "success_rate": self.config.performance.success_rate,
            },
        }

        with open(self.test_env.config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

    @asynccontextmanager
    async def database_session(self):
        """Get database session context manager."""
        if not self.db_engine:
            raise RuntimeError("Database not initialized")

        async_session = sessionmaker(
            self.db_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def clear_redis_cache(self):
        """Clear Redis cache for testing."""
        if self.redis_client:
            await self.redis_client.flushdb()


class TestDataGenerator:
    """Generates test data for ACGS testing."""

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash

    def generate_policy_data(self, policy_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock policy data."""
        import uuid

        policy_id = policy_id or str(uuid.uuid4())

        return {
            "policy_id": policy_id,
            "name": f"Test Policy {policy_id[:8]}",
            "version": "1.0.0",
            "description": "Generated test policy for E2E testing",
            "constitutional_hash": self.constitutional_hash,
            "rules": [
                {
                    "rule_id": str(uuid.uuid4()),
                    "condition": "test_condition",
                    "action": "test_action",
                    "priority": 1,
                }
            ],
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "created_by": "test_user",
                "tags": ["test", "e2e"],
            },
        }

    def generate_governance_request(
        self, request_type: str = "policy_validation"
    ) -> Dict[str, Any]:
        """Generate governance request data."""
        import uuid

        return {
            "request_id": str(uuid.uuid4()),
            "request_type": request_type,
            "constitutional_hash": self.constitutional_hash,
            "payload": {
                "policy_data": self.generate_policy_data(),
                "validation_level": "strict",
                "require_human_review": False,
            },
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "source": "e2e_test",
                "priority": "normal",
            },
        }

    def generate_agent_coordination_scenario(self) -> Dict[str, Any]:
        """Generate multi-agent coordination test scenario."""
        import uuid

        return {
            "scenario_id": str(uuid.uuid4()),
            "scenario_type": "policy_consensus",
            "constitutional_hash": self.constitutional_hash,
            "agents": [
                {
                    "agent_id": f"agent_{i}",
                    "agent_type": "governance_agent",
                    "capabilities": ["policy_analysis", "constitutional_review"],
                }
                for i in range(3)
            ],
            "coordination_task": {
                "task_type": "consensus_building",
                "target_policy": self.generate_policy_data(),
                "consensus_threshold": 0.7,
                "timeout_seconds": 30,
            },
            "expected_outcome": {
                "consensus_reached": True,
                "final_score": 0.85,
                "constitutional_compliance": True,
            },
        }

    def generate_performance_test_data(self, size: str = "medium") -> Dict[str, Any]:
        """Generate data for performance testing."""
        sizes = {
            "small": {"policies": 10, "requests": 100},
            "medium": {"policies": 100, "requests": 1000},
            "large": {"policies": 1000, "requests": 10000},
        }

        config = sizes.get(size, sizes["medium"])

        return {
            "test_size": size,
            "constitutional_hash": self.constitutional_hash,
            "policies": [
                self.generate_policy_data() for _ in range(config["policies"])
            ],
            "requests": [
                self.generate_governance_request() for _ in range(config["requests"])
            ],
            "performance_targets": {
                "max_latency_ms": 5.0,
                "min_throughput_rps": 100.0,
                "min_success_rate": 0.95,
            },
        }


class TestReportGenerator:
    """Generates comprehensive test reports."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_junit_xml(self, test_results: List[Dict[str, Any]]) -> Path:
        """Generate JUnit XML report."""
        from xml.dom import minidom
        from xml.etree.ElementTree import Element, SubElement, tostring

        testsuites = Element("testsuites")
        testsuite = SubElement(testsuites, "testsuite")

        testsuite.set("name", "ACGS E2E Tests")
        testsuite.set("tests", str(len(test_results)))
        testsuite.set(
            "failures", str(sum(1 for r in test_results if not r.get("success", True)))
        )
        testsuite.set(
            "time", str(sum(r.get("duration_ms", 0) for r in test_results) / 1000)
        )

        for result in test_results:
            testcase = SubElement(testsuite, "testcase")
            testcase.set("name", result.get("test_name", "unknown"))
            testcase.set("time", str(result.get("duration_ms", 0) / 1000))

            if not result.get("success", True):
                failure = SubElement(testcase, "failure")
                failure.set("message", result.get("error_message", "Test failed"))
                failure.text = result.get("error_message", "")

        # Pretty print XML
        rough_string = tostring(testsuites, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        output_file = self.output_dir / "junit.xml"
        with open(output_file, "w") as f:
            f.write(pretty_xml)

        return output_file

    def generate_html_report(
        self, test_results: List[Dict[str, Any]], summary: Dict[str, Any]
    ) -> Path:
        """Generate HTML test report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ACGS E2E Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .success { color: green; }
                .failure { color: red; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>ACGS E2E Test Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {total_tests}</p>
                <p>Passed: <span class="success">{passed_tests}</span></p>
                <p>Failed: <span class="failure">{failed_tests}</span></p>
                <p>Success Rate: {success_rate:.1%}</p>
                <p>Constitutional Compliance Rate: {constitutional_compliance_rate:.1%}</p>
                <p>Total Duration: {total_duration_ms:.0f}ms</p>
            </div>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration (ms)</th>
                    <th>Constitutional Compliance</th>
                    <th>Error Message</th>
                </tr>
                {test_rows}
            </table>
        </body>
        </html>
        """

        test_rows = ""
        for result in test_results:
            status = "PASS" if result.get("success", True) else "FAIL"
            status_class = "success" if result.get("success", True) else "failure"
            compliance = result.get("constitutional_compliance", "N/A")

            test_rows += f"""
                <tr>
                    <td>{result.get('test_name', 'unknown')}</td>
                    <td class="{status_class}">{status}</td>
                    <td>{result.get('duration_ms', 0):.1f}</td>
                    <td>{compliance}</td>
                    <td>{result.get('error_message', '')}</td>
                </tr>
            """

        html_content = html_template.format(test_rows=test_rows, **summary)

        output_file = self.output_dir / "report.html"
        with open(output_file, "w") as f:
            f.write(html_content)

        return output_file
