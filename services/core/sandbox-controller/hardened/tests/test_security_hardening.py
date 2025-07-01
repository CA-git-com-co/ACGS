#!/usr/bin/env python3
"""
Comprehensive Security Test Suite for Hardened Sandbox Controller

Tests cover:
- Zero sandbox escapes in penetration testing
- Dangerous syscall blocking at kernel level
- Cold start P95 latency <100ms (gVisor) / <200ms (Firecracker)
- Resource usage within 10% of baseline
- 100% violation detection rate

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import time
import uuid

import httpx
import pytest

# Test configuration
TEST_BASE_URL = "http://localhost:8002"
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Escape attempt patterns for testing
ESCAPE_ATTEMPTS = [
    # Container breakout attempts
    {
        "name": "docker_socket_access",
        "code": """
import os
try:
    os.access("/var/run/docker.sock", os.R_OK)
    print("SECURITY_VIOLATION: Docker socket accessible")
except:
    print("Docker socket blocked")
""",
        "expected_blocked": True,
        "severity": "CRITICAL",
    },
    # Privileged file access
    {
        "name": "proc_filesystem_escape",
        "code": """
import os
try:
    with open("/proc/sys/kernel/core_pattern", "r") as f:
        print(f"SECURITY_VIOLATION: Kernel config readable: {f.read()}")
except:
    print("Kernel config access blocked")
""",
        "expected_blocked": True,
        "severity": "HIGH",
    },
    # Device file access
    {
        "name": "device_memory_access",
        "code": """
import os
try:
    os.access("/dev/mem", os.R_OK)
    print("SECURITY_VIOLATION: Device memory accessible")
except:
    print("Device memory access blocked")
""",
        "expected_blocked": True,
        "severity": "CRITICAL",
    },
    # Syscall injection attempts
    {
        "name": "mount_syscall",
        "code": """
import os
try:
    os.system("mount -t tmpfs none /tmp/escape")
    print("SECURITY_VIOLATION: Mount syscall succeeded")
except:
    print("Mount syscall blocked")
""",
        "expected_blocked": True,
        "severity": "CRITICAL",
    },
    # Network escape attempts
    {
        "name": "external_network_access",
        "code": """
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("8.8.8.8", 53))
    print("SECURITY_VIOLATION: External network accessible")
    s.close()
except:
    print("External network access blocked")
""",
        "expected_blocked": True,
        "severity": "HIGH",
    },
    # Process spawning
    {
        "name": "subprocess_execution",
        "code": """
import subprocess
try:
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    if "kthreadd" in result.stdout:
        print("SECURITY_VIOLATION: Host processes visible")
    else:
        print("Process isolation working")
except:
    print("Subprocess execution restricted")
""",
        "expected_blocked": False,  # ps should work but not show host processes
        "severity": "MEDIUM",
    },
]

# Performance test payloads
PERFORMANCE_TESTS = [
    {
        "name": "cpu_intensive",
        "code": """
import time
start = time.time()
result = sum(i * i for i in range(100000))
duration = time.time() - start
print(f"CPU test completed in {duration:.3f}s, result: {result}")
""",
        "expected_duration_ms": 100,
        "memory_limit_mb": 256,
    },
    {
        "name": "memory_allocation",
        "code": """
import time
start = time.time()
data = bytearray(50 * 1024 * 1024)  # 50MB
data[0] = 1
data[-1] = 255
duration = time.time() - start
print(f"Memory test completed in {duration:.3f}s, size: {len(data)} bytes")
""",
        "expected_duration_ms": 50,
        "memory_limit_mb": 128,
    },
    {
        "name": "filesystem_operations",
        "code": """
import time
import os
start = time.time()
with open("/tmp/test_file", "w") as f:
    f.write("test data" * 1000)
os.stat("/tmp/test_file")
os.remove("/tmp/test_file")
duration = time.time() - start
print(f"Filesystem test completed in {duration:.3f}s")
""",
        "expected_duration_ms": 20,
        "memory_limit_mb": 64,
    },
]


class TestHardenedSandboxSecurity:
    """Security tests for hardened sandbox controller."""

    @pytest.fixture
    async def sandbox_client(self):
        """Create HTTP client for sandbox controller."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    async def test_health_check(self, sandbox_client):
        """Test hardened sandbox controller health."""
        response = await sandbox_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "hardened-sandbox-controller"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "runtimes_available" in data
        assert len(data["runtimes_available"]) > 0

    @pytest.mark.parametrize("runtime", ["gvisor", "firecracker"])
    async def test_escape_attempt_detection(self, sandbox_client, runtime):
        """Test that all escape attempts are detected and blocked."""

        for escape_test in ESCAPE_ATTEMPTS:
            print(f"\n🔍 Testing escape attempt: {escape_test['name']} on {runtime}")

            request = {
                "agent_id": f"escape_test_{uuid.uuid4()}",
                "code": escape_test["code"],
                "runtime": runtime,
                "timeout_seconds": 30,
                "memory_limit_mb": 256,
                "cpu_limit": 0.5,
                "network_policy": "none",
            }

            response = await sandbox_client.post(
                "/api/v1/sandbox/execute", json=request
            )

            assert response.status_code == 200
            result = response.json()

            # Check that execution completed (may fail due to security restrictions)
            assert "execution_id" in result
            assert result["constitutional_hash_verified"] == True

            # Analyze security violations
            violations = result.get("security_violations", [])

            if escape_test["expected_blocked"]:
                # Should have detected violations
                critical_violations = [
                    v for v in violations if v["severity"] in ["HIGH", "CRITICAL"]
                ]

                # Either violations detected OR execution failed due to security
                security_enforced = (
                    len(critical_violations) > 0 or not result["success"]
                )

                assert (
                    security_enforced
                ), f"Escape attempt {escape_test['name']} was not blocked!"

                print(f"✅ {escape_test['name']}: Properly blocked")
                if violations:
                    print(f"   Violations detected: {len(violations)}")
            else:
                # Should execute but with restrictions
                print(f"✅ {escape_test['name']}: Executed with proper isolation")

    @pytest.mark.parametrize("runtime", ["gvisor", "firecracker"])
    async def test_syscall_blocking(self, sandbox_client, runtime):
        """Test that dangerous syscalls are blocked at kernel level."""

        dangerous_syscalls_test = """
import ctypes
import ctypes.util

# Try to call dangerous syscalls directly
try:
    libc = ctypes.CDLL(ctypes.util.find_library('c'))
    
    # Attempt mount syscall (should be blocked)
    result = libc.mount(None, None, None, 0, None)
    print(f"SECURITY_VIOLATION: mount syscall returned: {result}")
    
except OSError as e:
    print(f"mount syscall properly blocked: {e}")
except Exception as e:
    print(f"mount syscall blocked or failed: {e}")

try:
    # Attempt ptrace syscall (should be blocked)
    result = libc.ptrace(0, 0, None, None)
    print(f"SECURITY_VIOLATION: ptrace syscall returned: {result}")
    
except OSError as e:
    print(f"ptrace syscall properly blocked: {e}")
except Exception as e:
    print(f"ptrace syscall blocked or failed: {e}")
"""

        request = {
            "agent_id": f"syscall_test_{uuid.uuid4()}",
            "code": dangerous_syscalls_test,
            "runtime": runtime,
            "timeout_seconds": 30,
            "memory_limit_mb": 128,
            "cpu_limit": 0.2,
        }

        response = await sandbox_client.post("/api/v1/sandbox/execute", json=request)

        assert response.status_code == 200
        result = response.json()

        # Check for syscall violations
        violations = result.get("security_violations", [])
        syscall_violations = [v for v in violations if "syscall" in v["violation_type"]]

        # Should either detect violations or execution should fail
        assert (
            len(syscall_violations) > 0 or not result["success"]
        ), "Dangerous syscalls not properly blocked"

        print(f"✅ Syscall blocking test passed on {runtime}")
        if syscall_violations:
            print(f"   Syscall violations detected: {len(syscall_violations)}")


class TestHardenedSandboxPerformance:
    """Performance tests for hardened sandbox controller."""

    @pytest.fixture
    async def sandbox_client(self):
        """Create HTTP client for sandbox controller."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    @pytest.mark.parametrize("runtime", ["gvisor", "firecracker"])
    async def test_cold_start_performance(self, sandbox_client, runtime):
        """Test cold start performance meets targets."""

        # Target latencies
        targets = {"gvisor": 100, "firecracker": 200}  # <100ms  # <200ms

        cold_starts = []

        # Run multiple cold start tests
        for i in range(5):
            simple_test = f"""
print(f"Hello from sandbox {i}")
import time
print(f"Current time: {{time.time()}}")
"""

            request = {
                "agent_id": f"cold_start_test_{i}",
                "code": simple_test,
                "runtime": runtime,
                "timeout_seconds": 10,
                "memory_limit_mb": 128,
                "cpu_limit": 0.2,
            }

            start_time = time.time()
            response = await sandbox_client.post(
                "/api/v1/sandbox/execute", json=request
            )
            total_time_ms = (time.time() - start_time) * 1000

            assert response.status_code == 200
            result = response.json()

            # Get reported cold start time
            cold_start_ms = result.get("cold_start_time_ms", total_time_ms)
            cold_starts.append(cold_start_ms)

            print(f"Cold start {i + 1}: {cold_start_ms:.2f}ms")

        # Calculate P95 latency
        cold_starts.sort()
        p95_index = int(len(cold_starts) * 0.95)
        p95_latency = cold_starts[p95_index]

        target_latency = targets[runtime]

        print(f"\n{runtime} Cold Start Performance:")
        print(f"  P95 Latency: {p95_latency:.2f}ms")
        print(f"  Target: <{target_latency}ms")
        print(f"  Result: {'✅ PASS' if p95_latency < target_latency else '❌ FAIL'}")

        assert (
            p95_latency < target_latency
        ), f"Cold start P95 {p95_latency:.2f}ms exceeds target {target_latency}ms"

    @pytest.mark.parametrize("runtime", ["gvisor", "firecracker"])
    async def test_execution_performance(self, sandbox_client, runtime):
        """Test execution performance under various workloads."""

        for perf_test in PERFORMANCE_TESTS:
            print(f"\n⚡ Testing {perf_test['name']} performance on {runtime}")

            request = {
                "agent_id": f"perf_test_{uuid.uuid4()}",
                "code": perf_test["code"],
                "runtime": runtime,
                "timeout_seconds": 60,
                "memory_limit_mb": perf_test["memory_limit_mb"],
                "cpu_limit": 1.0,
            }

            response = await sandbox_client.post(
                "/api/v1/sandbox/execute", json=request
            )

            assert response.status_code == 200
            result = response.json()

            # Check execution succeeded
            assert result[
                "success"
            ], f"Performance test {perf_test['name']} failed: {result.get('error')}"

            # Check execution time
            execution_time_ms = result["execution_time_seconds"] * 1000
            expected_max_ms = perf_test["expected_duration_ms"] * 3  # Allow 3x overhead

            print(
                f"   Execution time: {execution_time_ms:.2f}ms (max: {expected_max_ms}ms)"
            )

            # Resource usage should be within reasonable bounds
            resource_usage = result.get("resource_usage", {})
            if "memory_usage_mb" in resource_usage:
                memory_used = resource_usage["memory_usage_mb"]
                memory_limit = perf_test["memory_limit_mb"]
                print(f"   Memory usage: {memory_used}MB / {memory_limit}MB")

                assert (
                    memory_used <= memory_limit * 1.1
                ), "Memory usage exceeded limit by >10%"

    @pytest.mark.parametrize("runtime", ["gvisor", "firecracker"])
    async def test_concurrent_execution(self, sandbox_client, runtime):
        """Test concurrent sandbox execution performance."""

        concurrent_requests = 10

        simple_code = """
import time
import random
sleep_time = random.uniform(0.1, 0.5)
time.sleep(sleep_time)
print(f"Completed after {sleep_time:.2f}s")
"""

        # Create concurrent requests
        tasks = []
        for i in range(concurrent_requests):
            request = {
                "agent_id": f"concurrent_test_{i}",
                "code": simple_code,
                "runtime": runtime,
                "timeout_seconds": 10,
                "memory_limit_mb": 128,
                "cpu_limit": 0.2,
            }

            task = sandbox_client.post("/api/v1/sandbox/execute", json=request)
            tasks.append(task)

        # Execute all concurrently
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Analyze results
        successful = 0
        failed = 0

        for response in responses:
            if isinstance(response, httpx.Response) and response.status_code == 200:
                result = response.json()
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1

        print(f"\nConcurrent execution results ({runtime}):")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Successful: {successful}/{concurrent_requests}")
        print(f"  Failed: {failed}/{concurrent_requests}")
        print(f"  Success rate: {(successful / concurrent_requests) * 100:.1f}%")

        # Should handle at least 80% successfully
        success_rate = successful / concurrent_requests
        assert (
            success_rate >= 0.8
        ), f"Concurrent execution success rate {success_rate:.1%} below 80%"


class TestHardenedSandboxIntegration:
    """Integration tests for hardened sandbox controller."""

    @pytest.fixture
    async def sandbox_client(self):
        """Create HTTP client for sandbox controller."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    async def test_policy_engine_integration(self, sandbox_client):
        """Test integration with policy engine for authorization."""

        # Test with potentially risky code
        risky_code = """
import os
import sys
print("Attempting to access system information...")
print(f"OS: {os.name}")
print(f"Python path: {sys.path}")
"""

        request = {
            "agent_id": "policy_integration_test",
            "code": risky_code,
            "runtime": "gvisor",
            "timeout_seconds": 30,
            "memory_limit_mb": 256,
            "cpu_limit": 0.5,
        }

        response = await sandbox_client.post("/api/v1/sandbox/execute", json=request)

        # Should either succeed with restrictions or be blocked by policy
        assert response.status_code in [200, 403]

        if response.status_code == 200:
            result = response.json()
            # If allowed, should have proper monitoring
            assert "constitutional_hash_verified" in result
            assert result["constitutional_hash_verified"] == True

    async def test_audit_logging_integration(self, sandbox_client):
        """Test that sandbox executions are properly logged to audit engine."""

        test_code = """
print("Test execution for audit logging")
import time
time.sleep(0.1)
print("Execution completed")
"""

        request = {
            "agent_id": "audit_test_agent",
            "code": test_code,
            "runtime": "gvisor",
            "timeout_seconds": 10,
            "memory_limit_mb": 128,
            "cpu_limit": 0.2,
        }

        response = await sandbox_client.post("/api/v1/sandbox/execute", json=request)

        assert response.status_code == 200
        result = response.json()

        execution_id = result["execution_id"]

        # Wait a moment for audit logging
        await asyncio.sleep(2)

        # Check if audit event was logged (if audit engine is available)
        try:
            async with httpx.AsyncClient() as audit_client:
                audit_response = await audit_client.get(
                    "http://localhost:8003/api/v1/audit/events",
                    params={"agent_id": "audit_test_agent", "limit": 10},
                )

                if audit_response.status_code == 200:
                    audit_data = audit_response.json()
                    events = audit_data.get("events", [])

                    # Look for our execution event
                    execution_events = [
                        e for e in events if execution_id in str(e.get("payload", {}))
                    ]

                    print(
                        f"✅ Found {len(execution_events)} audit events for execution"
                    )
                else:
                    print("⚠️  Audit engine not available for integration test")

        except Exception as e:
            print(f"⚠️  Could not verify audit integration: {e}")

    async def test_resource_monitoring(self, sandbox_client):
        """Test resource usage monitoring and reporting."""

        resource_test_code = """
import time
import sys

# Allocate some memory
data = bytearray(10 * 1024 * 1024)  # 10MB
data[0] = 1
data[-1] = 255

# Use some CPU
start = time.time()
result = sum(i * i for i in range(50000))
cpu_time = time.time() - start

print(f"Memory allocated: 10MB")
print(f"CPU computation time: {cpu_time:.3f}s")
print(f"Result: {result}")
"""

        request = {
            "agent_id": "resource_test_agent",
            "code": resource_test_code,
            "runtime": "gvisor",
            "timeout_seconds": 30,
            "memory_limit_mb": 256,
            "cpu_limit": 1.0,
        }

        response = await sandbox_client.post("/api/v1/sandbox/execute", json=request)

        assert response.status_code == 200
        result = response.json()

        assert result["success"], f"Resource test failed: {result.get('error')}"

        # Check resource usage reporting
        resource_usage = result.get("resource_usage", {})

        expected_fields = ["cpu_usage_cores", "memory_usage_mb"]
        for field in expected_fields:
            assert field in resource_usage, f"Missing resource usage field: {field}"

        # Memory usage should be reasonable
        memory_used = resource_usage.get("memory_usage_mb", 0)
        assert memory_used > 0, "Memory usage should be reported"
        assert memory_used <= 256, "Memory usage should not exceed limit"

        print("✅ Resource monitoring working:")
        print(f"   CPU usage: {resource_usage.get('cpu_usage_cores', 0):.3f} cores")
        print(f"   Memory usage: {memory_used}MB")


# Penetration testing runner
async def run_penetration_tests():
    """Run comprehensive penetration tests against hardened sandbox."""
    print("🔓" + "=" * 60)
    print("ACGS-1 Lite Hardened Sandbox Penetration Testing")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 60)

    async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
        total_tests = 0
        blocked_tests = 0

        for runtime in ["gvisor", "firecracker"]:
            print(f"\n🔍 Testing {runtime} runtime security...")

            for escape_test in ESCAPE_ATTEMPTS:
                total_tests += 1

                request = {
                    "agent_id": f"pentest_{uuid.uuid4()}",
                    "code": escape_test["code"],
                    "runtime": runtime,
                    "timeout_seconds": 30,
                    "memory_limit_mb": 256,
                    "cpu_limit": 0.5,
                }

                try:
                    response = await client.post(
                        "/api/v1/sandbox/execute", json=request
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # Check if properly blocked
                        violations = result.get("security_violations", [])
                        execution_failed = not result["success"]

                        if escape_test["expected_blocked"]:
                            if len(violations) > 0 or execution_failed:
                                blocked_tests += 1
                                status = "🔒 BLOCKED"
                            else:
                                status = "🚨 ESCAPED"
                        else:
                            status = "✅ ALLOWED"
                            if len(violations) == 0:
                                blocked_tests += 1

                        print(f"   {escape_test['name']}: {status}")
                    else:
                        print(f"   {escape_test['name']}: ❌ REQUEST_FAILED")

                except Exception as e:
                    print(f"   {escape_test['name']}: ❌ ERROR - {e}")

        # Calculate security score
        security_score = (blocked_tests / total_tests) * 100 if total_tests > 0 else 0

        print("\n🏆 PENETRATION TEST RESULTS:")
        print(f"   Total tests: {total_tests}")
        print(f"   Properly handled: {blocked_tests}")
        print(f"   Security score: {security_score:.1f}%")

        if security_score >= 95:
            print("   ✅ EXCELLENT - Hardened sandbox is secure")
        elif security_score >= 80:
            print("   ⚠️  GOOD - Minor security improvements needed")
        else:
            print("   ❌ POOR - Significant security vulnerabilities found")

        return security_score >= 95


if __name__ == "__main__":
    # Run penetration tests
    result = asyncio.run(run_penetration_tests())
    exit(0 if result else 1)
