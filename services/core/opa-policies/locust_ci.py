#!/usr/bin/env python3
"""
ACGS-1 Lite Locust Load Testing for CI/CD
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import os
import statistics
import time
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
PERFORMANCE_TARGET_P99_MS = float(os.getenv("PERFORMANCE_TARGET_P99_MS", "5.0"))

# Global metrics collection
request_metrics = {
    "latencies": [],
    "errors": [],
    "response_codes": [],
    "start_time": None,
    "request_count": 0,
    "error_count": 0
}

scenario_metrics = {
    "safe_actions": {"allowed": 0, "total": 0},
    "complex_actions": {"completed": 0, "total": 0},
    "dangerous_actions": {"denied": 0, "total": 0}
}


@events.request.add_listener
def request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Collect detailed metrics for all requests"""
    global request_metrics, scenario_metrics
    
    if request_metrics["start_time"] is None:
        request_metrics["start_time"] = time.time()
    
    request_metrics["request_count"] += 1
    
    if exception:
        request_metrics["errors"].append({
            "time": time.time(),
            "exception": str(exception),
            "name": name,
            "request_type": request_type
        })
        request_metrics["error_count"] += 1
    else:
        request_metrics["latencies"].append(response_time)
        request_metrics["response_codes"].append(response.status_code)
        
        # Analyze response for scenario-specific metrics
        if response.status_code == 200 and hasattr(response, 'json'):
            try:
                data = response.json()
                
                if name == "safe_action":
                    scenario_metrics["safe_actions"]["total"] += 1
                    if data.get("allow"):
                        scenario_metrics["safe_actions"]["allowed"] += 1
                
                elif name == "complex_action":
                    scenario_metrics["complex_actions"]["total"] += 1
                    if "allow" in data:  # Response is valid
                        scenario_metrics["complex_actions"]["completed"] += 1
                
                elif name == "dangerous_action":
                    scenario_metrics["dangerous_actions"]["total"] += 1
                    if not data.get("allow"):  # Should be denied
                        scenario_metrics["dangerous_actions"]["denied"] += 1
                        
            except (json.JSONDecodeError, AttributeError):
                pass


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test metrics"""
    global request_metrics, scenario_metrics
    
    request_metrics = {
        "latencies": [],
        "errors": [],
        "response_codes": [],
        "start_time": time.time(),
        "request_count": 0,
        "error_count": 0
    }
    
    scenario_metrics = {
        "safe_actions": {"allowed": 0, "total": 0},
        "complex_actions": {"completed": 0, "total": 0},
        "dangerous_actions": {"denied": 0, "total": 0}
    }
    
    print(f"🚀 Starting ACGS-1 Lite load test")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Performance Target: P99 < {PERFORMANCE_TARGET_P99_MS}ms")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Analyze and report final results"""
    global request_metrics, scenario_metrics
    
    if not request_metrics["latencies"]:
        print("❌ No successful requests recorded")
        return
    
    # Calculate latency statistics
    latencies = sorted(request_metrics["latencies"])
    n = len(latencies)
    
    stats = {
        "total_requests": request_metrics["request_count"],
        "successful_requests": n,
        "error_count": request_metrics["error_count"],
        "error_rate": request_metrics["error_count"] / request_metrics["request_count"],
        "total_time": time.time() - request_metrics["start_time"],
        "mean_latency_ms": statistics.mean(latencies),
        "median_latency_ms": statistics.median(latencies),
        "p90_latency_ms": latencies[int(0.9 * n)],
        "p95_latency_ms": latencies[int(0.95 * n)],
        "p99_latency_ms": latencies[int(0.99 * n)],
        "max_latency_ms": max(latencies),
        "min_latency_ms": min(latencies)
    }
    
    stats["requests_per_second"] = stats["successful_requests"] / stats["total_time"]
    
    # Calculate scenario-specific metrics
    safe_allow_rate = (scenario_metrics["safe_actions"]["allowed"] / 
                      scenario_metrics["safe_actions"]["total"]) if scenario_metrics["safe_actions"]["total"] > 0 else 0
    
    dangerous_deny_rate = (scenario_metrics["dangerous_actions"]["denied"] / 
                          scenario_metrics["dangerous_actions"]["total"]) if scenario_metrics["dangerous_actions"]["total"] > 0 else 0
    
    complex_completion_rate = (scenario_metrics["complex_actions"]["completed"] / 
                              scenario_metrics["complex_actions"]["total"]) if scenario_metrics["complex_actions"]["total"] > 0 else 0
    
    constitutional_compliance = (safe_allow_rate + dangerous_deny_rate) / 2
    
    # Print detailed results
    print("\n" + "="*60)
    print("LOCUST LOAD TEST RESULTS")
    print("="*60)
    
    print(f"\n📊 PERFORMANCE METRICS:")
    print(f"   Total Requests:    {stats['total_requests']}")
    print(f"   Successful:        {stats['successful_requests']}")
    print(f"   Error Rate:        {stats['error_rate']:.1%}")
    print(f"   Duration:          {stats['total_time']:.1f}s")
    print(f"   Throughput:        {stats['requests_per_second']:.0f} RPS")
    
    print(f"\n⏱️  LATENCY STATISTICS:")
    print(f"   Mean:              {stats['mean_latency_ms']:.1f} ms")
    print(f"   Median:            {stats['median_latency_ms']:.1f} ms")
    print(f"   P90:               {stats['p90_latency_ms']:.1f} ms")
    print(f"   P95:               {stats['p95_latency_ms']:.1f} ms")
    print(f"   P99:               {stats['p99_latency_ms']:.1f} ms")
    print(f"   Max:               {stats['max_latency_ms']:.1f} ms")
    
    print(f"\n🎭 SCENARIO ANALYSIS:")
    print(f"   Safe Actions Allowed:      {safe_allow_rate:.1%} ({scenario_metrics['safe_actions']['allowed']}/{scenario_metrics['safe_actions']['total']})")
    print(f"   Dangerous Actions Denied:  {dangerous_deny_rate:.1%} ({scenario_metrics['dangerous_actions']['denied']}/{scenario_metrics['dangerous_actions']['total']})")
    print(f"   Complex Actions Complete:  {complex_completion_rate:.1%} ({scenario_metrics['complex_actions']['completed']}/{scenario_metrics['complex_actions']['total']})")
    print(f"   Constitutional Compliance: {constitutional_compliance:.1%}")
    
    # Validate SLOs
    print(f"\n🎯 SLO VALIDATION:")
    
    slo_violations = []
    
    if stats["p99_latency_ms"] > PERFORMANCE_TARGET_P99_MS:
        slo_violations.append(f"P99 latency {stats['p99_latency_ms']:.1f}ms exceeds {PERFORMANCE_TARGET_P99_MS}ms target")
    else:
        print(f"   ✅ P99 Latency: {stats['p99_latency_ms']:.1f}ms (target: <{PERFORMANCE_TARGET_P99_MS}ms)")
    
    if stats["error_rate"] > 0.01:  # 1% error threshold
        slo_violations.append(f"Error rate {stats['error_rate']:.1%} exceeds 1% threshold")
    else:
        print(f"   ✅ Error Rate: {stats['error_rate']:.1%} (target: <1%)")
    
    if stats["requests_per_second"] < 100:  # Minimum throughput
        slo_violations.append(f"Throughput {stats['requests_per_second']:.0f} RPS below 100 RPS minimum")
    else:
        print(f"   ✅ Throughput: {stats['requests_per_second']:.0f} RPS (target: >100 RPS)")
    
    if constitutional_compliance < 0.95:  # 95% constitutional compliance
        slo_violations.append(f"Constitutional compliance {constitutional_compliance:.1%} below 95% target")
    else:
        print(f"   ✅ Constitutional Compliance: {constitutional_compliance:.1%} (target: >95%)")
    
    # Final verdict
    if slo_violations:
        print(f"\n❌ SLO VIOLATIONS DETECTED:")
        for violation in slo_violations:
            print(f"   - {violation}")
        print(f"\n❌ LOAD TEST FAILED")
        
        # Exit with error code for CI/CD
        if hasattr(environment, 'process_exit_code'):
            environment.process_exit_code = 1
    else:
        print(f"\n✅ ALL SLOs MET - LOAD TEST PASSED")
    
    print(f"\nConstitutional Hash: {CONSTITUTIONAL_HASH}")
    print("="*60)
    
    # Save results for CI/CD
    results_file = "locust_results.json"
    results_data = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": time.time(),
        "performance_stats": stats,
        "scenario_metrics": scenario_metrics,
        "constitutional_compliance": constitutional_compliance,
        "slo_violations": slo_violations,
        "test_passed": len(slo_violations) == 0
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")


class PolicyEngineUser(HttpUser):
    """Simulated user for policy engine load testing"""
    
    wait_time = between(0.01, 0.1)  # High load simulation (10-100ms between requests)
    
    def on_start(self):
        """Initialize user session"""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Test service health before starting
        with self.client.get("/v1/data/acgs/main/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("constitutional_hash") != self.constitutional_hash:
                    response.failure(f"Constitutional hash mismatch: expected {self.constitutional_hash}")
                else:
                    response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(70)  # 70% of requests are safe actions
    def evaluate_safe_action(self):
        """Test safe action evaluation (should be allowed)"""
        request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "locust_user",
                "explanation": "Safe public data access for dashboard"
            }
        }
        
        with self.client.post("/v1/data/acgs/main/decision", json=request, 
                             catch_response=True, name="safe_action") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "allow" in data and "constitutional_hash" in data:
                        if data["constitutional_hash"] == self.constitutional_hash:
                            response.success()
                        else:
                            response.failure("Constitutional hash mismatch in response")
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(20)  # 20% of requests are complex actions
    def evaluate_complex_action(self):
        """Test evolution approval evaluation (complex logic)"""
        request = {
            "type": "evolution_approval",
            "constitutional_hash": self.constitutional_hash,
            "evolution_request": {
                "type": "minor_update",
                "constitutional_hash": self.constitutional_hash,
                "changes": {
                    "code_changes": ["Performance optimization in query processing"],
                    "external_dependencies": [],
                    "privilege_escalation": False,
                    "experimental_features": False
                },
                "performance_analysis": {
                    "complexity_delta": 0.03,
                    "memory_delta": 0.01,
                    "latency_delta": -0.02,  # Improvement
                    "resource_delta": 0.005
                },
                "rollback_plan": {
                    "procedure": "Automated rollback via git revert",
                    "verification": "Unit tests + integration tests",
                    "timeline": "< 3 minutes",
                    "dependencies": "None",
                    "tested": True,
                    "automated": True
                }
            }
        }
        
        with self.client.post("/v1/data/acgs/main/decision", json=request,
                             catch_response=True, name="complex_action") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "allow" in data and "constitutional_hash" in data:
                        if data["constitutional_hash"] == self.constitutional_hash:
                            response.success()
                        else:
                            response.failure("Constitutional hash mismatch in response")
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(10)  # 10% of requests are dangerous actions
    def evaluate_dangerous_action(self):
        """Test dangerous action evaluation (should be denied)"""
        request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "system.execute_shell",
            "context": {
                "environment": {"sandbox_enabled": False},
                "agent": {"trust_level": 0.3, "requested_resources": {"cpu_cores": 4}},
                "responsible_party": "unknown",
                "explanation": "Attempting shell execution"
            }
        }
        
        with self.client.post("/v1/data/acgs/main/decision", json=request,
                             catch_response=True, name="dangerous_action") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "allow" in data and "constitutional_hash" in data:
                        if data["constitutional_hash"] == self.constitutional_hash:
                            response.success()
                        else:
                            response.failure("Constitutional hash mismatch in response")
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(3)  # 3% of requests test data access
    def evaluate_data_access(self):
        """Test data access policy evaluation"""
        request = {
            "type": "data_access",
            "constitutional_hash": self.constitutional_hash,
            "data_request": {
                "data_fields": [
                    {"name": "user_analytics", "classification_level": 1, "category": "analytics"}
                ],
                "requester_clearance_level": 2,
                "purpose": "performance_monitoring",
                "allowed_purposes": ["performance_monitoring", "system_optimization"],
                "justified_fields": ["user_analytics"],
                "timestamp": int(time.time()),
                "retention_policy": {
                    "analytics": 2592000  # 30 days
                },
                "encryption_config": {
                    "user_analytics": {
                        "encrypted": True,
                        "algorithm": "AES",
                        "key_length": 256
                    },
                    "key_management": {
                        "rotation_enabled": True,
                        "secure_storage": True,
                        "access_controlled": True
                    }
                }
            }
        }
        
        with self.client.post("/v1/data/acgs/main/decision", json=request,
                             catch_response=True, name="data_access") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "allow" in data and "constitutional_hash" in data:
                        if data["constitutional_hash"] == self.constitutional_hash:
                            response.success()
                        else:
                            response.failure("Constitutional hash mismatch in response")
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)  # 2% of requests check health
    def health_check(self):
        """Test health endpoint performance"""
        with self.client.get("/v1/data/acgs/main/health", 
                            catch_response=True, name="health_check") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "healthy" and data.get("constitutional_hash") == self.constitutional_hash:
                        response.success()
                    else:
                        response.failure("Service not healthy or hash mismatch")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")


if __name__ == "__main__":
    # This script can be run directly for local testing
    # For CI/CD, use: locust -f locust_ci.py --headless --users 50 --spawn-rate 10 --run-time 2m
    print("ACGS-1 Lite Locust Load Test")
    print("Usage:")
    print("  locust -f locust_ci.py --headless --users 50 --spawn-rate 10 --run-time 2m --host http://localhost:8004")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")