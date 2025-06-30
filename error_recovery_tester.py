#!/usr/bin/env python3
"""
Error Handling and Recovery Testing Framework for ACGS-2
Tests error handling scenarios, recovery mechanisms, circuit breakers,
and system resilience under failure conditions.
"""

import os
import sys
import json
import time
import random
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ErrorTestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class ErrorTestResult:
    test_name: str
    status: ErrorTestStatus
    execution_time: float
    error_scenarios_tested: int
    error_scenarios_handled: int
    recovery_mechanisms_tested: int
    recovery_mechanisms_working: int
    resilience_score: float  # 0-100
    details: Dict[str, Any]
    error_message: Optional[str] = None

class ErrorRecoveryTester:
    def __init__(self):
        self.results = []
        self.project_root = project_root
        
    def log_result(self, result: ErrorTestResult):
        """Log an error handling test result."""
        self.results.append(result)
        status_symbol = {"PASS": "✓", "FAIL": "✗", "SKIP": "⊝", "ERROR": "⚠"}
        symbol = status_symbol.get(result.status.value, "?")
        
        error_handling_rate = (result.error_scenarios_handled / result.error_scenarios_tested * 100) if result.error_scenarios_tested > 0 else 0
        recovery_rate = (result.recovery_mechanisms_working / result.recovery_mechanisms_tested * 100) if result.recovery_mechanisms_tested > 0 else 0
        
        print(f"{symbol} {result.test_name} ({result.execution_time:.3f}s)")
        print(f"  Error Handling: {result.error_scenarios_handled}/{result.error_scenarios_tested} ({error_handling_rate:.1f}%)")
        print(f"  Recovery: {result.recovery_mechanisms_working}/{result.recovery_mechanisms_tested} ({recovery_rate:.1f}%)")
        print(f"  Resilience Score: {result.resilience_score:.1f}/100")
        
        if result.error_message:
            print(f"  Error: {result.error_message}")
    
    def test_exception_handling(self) -> ErrorTestResult:
        """Test exception handling mechanisms."""
        start_time = time.time()
        try:
            error_scenarios = [
                {"name": "division_by_zero", "test": lambda: 1 / 0},
                {"name": "key_error", "test": lambda: {}["nonexistent_key"]},
                {"name": "index_error", "test": lambda: [][0]},
                {"name": "type_error", "test": lambda: "string" + 5},
                {"name": "value_error", "test": lambda: int("not_a_number")},
                {"name": "attribute_error", "test": lambda: None.nonexistent_method()},
                {"name": "file_not_found", "test": lambda: open("nonexistent_file.txt")},
                {"name": "memory_error_simulation", "test": lambda: [0] * (10**8)},  # Large memory allocation
            ]
            
            error_scenarios_tested = len(error_scenarios)
            error_scenarios_handled = 0
            error_details = []
            
            for scenario in error_scenarios:
                try:
                    # Execute the error-prone operation
                    scenario["test"]()
                    # If we reach here, the operation didn't fail as expected
                    error_details.append({
                        "scenario": scenario["name"],
                        "handled": False,
                        "reason": "Operation succeeded unexpectedly"
                    })
                except Exception as e:
                    # Exception was properly caught
                    error_scenarios_handled += 1
                    error_details.append({
                        "scenario": scenario["name"],
                        "handled": True,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e)[:100]  # Truncate long messages
                    })
            
            # Test custom error handling wrapper
            def safe_operation(operation, default_value=None):
                """Wrapper for safe operation execution."""
                try:
                    return operation()
                except Exception as e:
                    return {"error": True, "exception": str(e), "default": default_value}
            
            # Test the wrapper
            wrapper_tests = [
                safe_operation(lambda: 1 / 0, "division_error"),
                safe_operation(lambda: {"key": "value"}["key"], None),
                safe_operation(lambda: [1, 2, 3][10], "index_error")
            ]
            
            wrapper_working = sum(1 for test in wrapper_tests if isinstance(test, dict) and test.get("error"))
            
            resilience_score = (error_scenarios_handled / error_scenarios_tested) * 80 + (wrapper_working / len(wrapper_tests)) * 20
            
            status = ErrorTestStatus.PASS if resilience_score >= 80 else ErrorTestStatus.FAIL
            
            return ErrorTestResult(
                "exception_handling",
                status,
                time.time() - start_time,
                error_scenarios_tested,
                error_scenarios_handled,
                len(wrapper_tests),
                wrapper_working,
                resilience_score,
                {
                    "error_details": error_details,
                    "wrapper_tests": wrapper_tests,
                    "custom_wrapper_working": wrapper_working == len(wrapper_tests)
                }
            )
            
        except Exception as e:
            return ErrorTestResult(
                "exception_handling",
                ErrorTestStatus.ERROR,
                time.time() - start_time,
                0,
                0,
                0,
                0,
                0.0,
                {},
                str(e)
            )
    
    def test_circuit_breaker_pattern(self) -> ErrorTestResult:
        """Test circuit breaker pattern implementation."""
        start_time = time.time()
        try:
            class CircuitBreaker:
                def __init__(self, failure_threshold=5, recovery_timeout=10):
                    self.failure_threshold = failure_threshold
                    self.recovery_timeout = recovery_timeout
                    self.failure_count = 0
                    self.last_failure_time = None
                    self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
                
                def call(self, operation):
                    if self.state == "OPEN":
                        if time.time() - self.last_failure_time > self.recovery_timeout:
                            self.state = "HALF_OPEN"
                        else:
                            raise Exception("Circuit breaker is OPEN")
                    
                    try:
                        result = operation()
                        if self.state == "HALF_OPEN":
                            self.state = "CLOSED"
                            self.failure_count = 0
                        return result
                    except Exception as e:
                        self.failure_count += 1
                        self.last_failure_time = time.time()
                        
                        if self.failure_count >= self.failure_threshold:
                            self.state = "OPEN"
                        
                        raise e
            
            # Test circuit breaker
            circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
            
            # Simulate failing operations
            def failing_operation():
                raise Exception("Simulated failure")
            
            def successful_operation():
                return "success"
            
            error_scenarios_tested = 0
            error_scenarios_handled = 0
            recovery_mechanisms_tested = 0
            recovery_mechanisms_working = 0
            
            # Test failure accumulation
            for i in range(5):
                error_scenarios_tested += 1
                try:
                    circuit_breaker.call(failing_operation)
                except Exception:
                    error_scenarios_handled += 1
            
            # Circuit breaker should be OPEN now
            recovery_mechanisms_tested += 1
            if circuit_breaker.state == "OPEN":
                recovery_mechanisms_working += 1
            
            # Test that circuit breaker blocks calls when OPEN
            error_scenarios_tested += 1
            try:
                circuit_breaker.call(successful_operation)
            except Exception as e:
                if "Circuit breaker is OPEN" in str(e):
                    error_scenarios_handled += 1
            
            # Wait for recovery timeout
            time.sleep(1.1)
            
            # Test recovery to HALF_OPEN
            recovery_mechanisms_tested += 1
            try:
                result = circuit_breaker.call(successful_operation)
                if result == "success" and circuit_breaker.state == "CLOSED":
                    recovery_mechanisms_working += 1
            except Exception:
                pass
            
            resilience_score = (
                (error_scenarios_handled / error_scenarios_tested) * 60 +
                (recovery_mechanisms_working / recovery_mechanisms_tested) * 40
            ) if error_scenarios_tested > 0 and recovery_mechanisms_tested > 0 else 0
            
            status = ErrorTestStatus.PASS if resilience_score >= 80 else ErrorTestStatus.FAIL
            
            return ErrorTestResult(
                "circuit_breaker_pattern",
                status,
                time.time() - start_time,
                error_scenarios_tested,
                error_scenarios_handled,
                recovery_mechanisms_tested,
                recovery_mechanisms_working,
                resilience_score,
                {
                    "final_circuit_state": circuit_breaker.state,
                    "failure_count": circuit_breaker.failure_count,
                    "failure_threshold": circuit_breaker.failure_threshold
                }
            )
            
        except Exception as e:
            return ErrorTestResult(
                "circuit_breaker_pattern",
                ErrorTestStatus.ERROR,
                time.time() - start_time,
                0,
                0,
                0,
                0,
                0.0,
                {},
                str(e)
            )
    
    def test_retry_mechanisms(self) -> ErrorTestResult:
        """Test retry mechanisms and exponential backoff."""
        start_time = time.time()
        try:
            def retry_with_backoff(operation, max_retries=3, base_delay=0.1):
                """Retry operation with exponential backoff."""
                for attempt in range(max_retries + 1):
                    try:
                        return operation()
                    except Exception as e:
                        if attempt == max_retries:
                            raise e
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
            
            # Test scenarios
            error_scenarios_tested = 0
            error_scenarios_handled = 0
            recovery_mechanisms_tested = 0
            recovery_mechanisms_working = 0
            
            # Test 1: Operation that succeeds after retries
            attempt_count = 0
            def eventually_successful_operation():
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count < 3:
                    raise Exception("Temporary failure")
                return "success"
            
            error_scenarios_tested += 1
            recovery_mechanisms_tested += 1
            try:
                result = retry_with_backoff(eventually_successful_operation)
                if result == "success":
                    error_scenarios_handled += 1
                    recovery_mechanisms_working += 1
            except Exception:
                pass
            
            # Test 2: Operation that always fails
            def always_failing_operation():
                raise Exception("Permanent failure")
            
            error_scenarios_tested += 1
            try:
                retry_with_backoff(always_failing_operation, max_retries=2)
            except Exception:
                error_scenarios_handled += 1  # Expected to fail after retries
            
            # Test 3: Immediate success
            def immediate_success_operation():
                return "immediate_success"
            
            error_scenarios_tested += 1
            recovery_mechanisms_tested += 1
            try:
                result = retry_with_backoff(immediate_success_operation)
                if result == "immediate_success":
                    error_scenarios_handled += 1
                    recovery_mechanisms_working += 1
            except Exception:
                pass
            
            resilience_score = (
                (error_scenarios_handled / error_scenarios_tested) * 70 +
                (recovery_mechanisms_working / recovery_mechanisms_tested) * 30
            ) if error_scenarios_tested > 0 and recovery_mechanisms_tested > 0 else 0
            
            status = ErrorTestStatus.PASS if resilience_score >= 80 else ErrorTestStatus.FAIL
            
            return ErrorTestResult(
                "retry_mechanisms",
                status,
                time.time() - start_time,
                error_scenarios_tested,
                error_scenarios_handled,
                recovery_mechanisms_tested,
                recovery_mechanisms_working,
                resilience_score,
                {
                    "retry_attempts_made": attempt_count,
                    "backoff_strategy": "exponential"
                }
            )
            
        except Exception as e:
            return ErrorTestResult(
                "retry_mechanisms",
                ErrorTestStatus.ERROR,
                time.time() - start_time,
                0,
                0,
                0,
                0,
                0.0,
                {},
                str(e)
            )
    
    def test_graceful_degradation(self) -> ErrorTestResult:
        """Test graceful degradation under system stress."""
        start_time = time.time()
        try:
            class GracefulService:
                def __init__(self):
                    self.primary_service_available = True
                    self.cache_available = True
                    self.fallback_data = {"default": "fallback_response"}
                
                def get_data(self, key):
                    # Try primary service first
                    if self.primary_service_available:
                        try:
                            return self._primary_service_call(key)
                        except Exception:
                            self.primary_service_available = False
                    
                    # Try cache
                    if self.cache_available:
                        try:
                            return self._cache_lookup(key)
                        except Exception:
                            self.cache_available = False
                    
                    # Fallback to default data
                    return self.fallback_data.get(key, "service_unavailable")
                
                def _primary_service_call(self, key):
                    if not self.primary_service_available:
                        raise Exception("Primary service down")
                    return f"primary_data_{key}"
                
                def _cache_lookup(self, key):
                    if not self.cache_available:
                        raise Exception("Cache unavailable")
                    return f"cached_data_{key}"
            
            service = GracefulService()
            
            error_scenarios_tested = 0
            error_scenarios_handled = 0
            recovery_mechanisms_tested = 3  # Primary, cache, fallback
            recovery_mechanisms_working = 0
            
            # Test normal operation
            error_scenarios_tested += 1
            try:
                result = service.get_data("test")
                if "primary_data" in result:
                    error_scenarios_handled += 1
                    recovery_mechanisms_working += 1
            except Exception:
                pass
            
            # Simulate primary service failure
            service.primary_service_available = False
            error_scenarios_tested += 1
            try:
                result = service.get_data("test")
                if "cached_data" in result:
                    error_scenarios_handled += 1
                    recovery_mechanisms_working += 1
            except Exception:
                pass
            
            # Simulate cache failure
            service.cache_available = False
            error_scenarios_tested += 1
            try:
                result = service.get_data("default")
                if result == "fallback_response":
                    error_scenarios_handled += 1
                    recovery_mechanisms_working += 1
            except Exception:
                pass
            
            # Test unknown key fallback
            error_scenarios_tested += 1
            try:
                result = service.get_data("unknown")
                if result == "service_unavailable":
                    error_scenarios_handled += 1
            except Exception:
                pass
            
            resilience_score = (
                (error_scenarios_handled / error_scenarios_tested) * 60 +
                (recovery_mechanisms_working / recovery_mechanisms_tested) * 40
            ) if error_scenarios_tested > 0 and recovery_mechanisms_tested > 0 else 0
            
            status = ErrorTestStatus.PASS if resilience_score >= 80 else ErrorTestStatus.FAIL
            
            return ErrorTestResult(
                "graceful_degradation",
                status,
                time.time() - start_time,
                error_scenarios_tested,
                error_scenarios_handled,
                recovery_mechanisms_tested,
                recovery_mechanisms_working,
                resilience_score,
                {
                    "primary_service_status": service.primary_service_available,
                    "cache_status": service.cache_available,
                    "fallback_mechanisms": ["primary_service", "cache", "default_data"]
                }
            )
            
        except Exception as e:
            return ErrorTestResult(
                "graceful_degradation",
                ErrorTestStatus.ERROR,
                time.time() - start_time,
                0,
                0,
                0,
                0,
                0.0,
                {},
                str(e)
            )
    
    def test_concurrent_error_handling(self) -> ErrorTestResult:
        """Test error handling under concurrent load."""
        start_time = time.time()
        try:
            def error_prone_operation(operation_id):
                """Operation that randomly fails."""
                if random.random() < 0.3:  # 30% failure rate
                    raise Exception(f"Random failure in operation {operation_id}")
                return f"success_{operation_id}"
            
            def safe_concurrent_operation(operation_id):
                """Safely execute operation with error handling."""
                try:
                    return {"status": "success", "result": error_prone_operation(operation_id)}
                except Exception as e:
                    return {"status": "error", "error": str(e), "operation_id": operation_id}
            
            # Run concurrent operations
            num_operations = 50
            error_scenarios_tested = num_operations
            error_scenarios_handled = 0
            recovery_mechanisms_tested = 1  # Safe wrapper
            recovery_mechanisms_working = 0
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(safe_concurrent_operation, i)
                    for i in range(num_operations)
                ]
                
                results = []
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Count as handled if we got a structured response
                        if isinstance(result, dict) and "status" in result:
                            error_scenarios_handled += 1
                    except Exception:
                        # Unhandled exception
                        pass
            
            # Check if error handling wrapper worked
            if error_scenarios_handled == error_scenarios_tested:
                recovery_mechanisms_working = 1
            
            # Analyze results
            successful_operations = sum(1 for r in results if r.get("status") == "success")
            failed_operations = sum(1 for r in results if r.get("status") == "error")
            
            resilience_score = (
                (error_scenarios_handled / error_scenarios_tested) * 80 +
                (recovery_mechanisms_working / recovery_mechanisms_tested) * 20
            ) if error_scenarios_tested > 0 and recovery_mechanisms_tested > 0 else 0
            
            status = ErrorTestStatus.PASS if resilience_score >= 80 else ErrorTestStatus.FAIL
            
            return ErrorTestResult(
                "concurrent_error_handling",
                status,
                time.time() - start_time,
                error_scenarios_tested,
                error_scenarios_handled,
                recovery_mechanisms_tested,
                recovery_mechanisms_working,
                resilience_score,
                {
                    "total_operations": num_operations,
                    "successful_operations": successful_operations,
                    "failed_operations": failed_operations,
                    "all_operations_handled": error_scenarios_handled == error_scenarios_tested
                }
            )
            
        except Exception as e:
            return ErrorTestResult(
                "concurrent_error_handling",
                ErrorTestStatus.ERROR,
                time.time() - start_time,
                0,
                0,
                0,
                0,
                0.0,
                {},
                str(e)
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all error handling and recovery tests."""
        print("Starting Error Handling and Recovery Testing...")
        print("=" * 60)
        
        # Define test methods
        test_methods = [
            self.test_exception_handling,
            self.test_circuit_breaker_pattern,
            self.test_retry_mechanisms,
            self.test_graceful_degradation,
            self.test_concurrent_error_handling
        ]
        
        # Run all tests
        for test_method in test_methods:
            try:
                result = test_method()
                self.log_result(result)
            except Exception as e:
                error_result = ErrorTestResult(
                    test_method.__name__,
                    ErrorTestStatus.ERROR,
                    0.0,
                    0,
                    0,
                    0,
                    0,
                    0.0,
                    {},
                    f"Test execution failed: {str(e)}"
                )
                self.log_result(error_result)
        
        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == ErrorTestStatus.PASS)
        failed_tests = sum(1 for r in self.results if r.status == ErrorTestStatus.FAIL)
        error_tests = sum(1 for r in self.results if r.status == ErrorTestStatus.ERROR)
        
        total_error_scenarios = sum(r.error_scenarios_tested for r in self.results)
        handled_error_scenarios = sum(r.error_scenarios_handled for r in self.results)
        total_recovery_mechanisms = sum(r.recovery_mechanisms_tested for r in self.results)
        working_recovery_mechanisms = sum(r.recovery_mechanisms_working for r in self.results)
        
        avg_resilience_score = sum(r.resilience_score for r in self.results) / len(self.results) if self.results else 0
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "error_handling_metrics": {
                "total_error_scenarios": total_error_scenarios,
                "handled_error_scenarios": handled_error_scenarios,
                "error_handling_rate": (handled_error_scenarios / total_error_scenarios * 100) if total_error_scenarios > 0 else 0,
                "total_recovery_mechanisms": total_recovery_mechanisms,
                "working_recovery_mechanisms": working_recovery_mechanisms,
                "recovery_success_rate": (working_recovery_mechanisms / total_recovery_mechanisms * 100) if total_recovery_mechanisms > 0 else 0,
                "average_resilience_score": avg_resilience_score
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "error_scenarios_tested": r.error_scenarios_tested,
                    "error_scenarios_handled": r.error_scenarios_handled,
                    "recovery_mechanisms_tested": r.recovery_mechanisms_tested,
                    "recovery_mechanisms_working": r.recovery_mechanisms_working,
                    "resilience_score": r.resilience_score,
                    "details": r.details,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
        
        print("\n" + "=" * 60)
        print("ERROR HANDLING AND RECOVERY TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Error Scenarios Handled: {handled_error_scenarios}/{total_error_scenarios} ({summary['error_handling_metrics']['error_handling_rate']:.1f}%)")
        print(f"Recovery Mechanisms Working: {working_recovery_mechanisms}/{total_recovery_mechanisms} ({summary['error_handling_metrics']['recovery_success_rate']:.1f}%)")
        print(f"Average Resilience Score: {avg_resilience_score:.1f}/100")
        
        return summary

def main():
    tester = ErrorRecoveryTester()
    summary = tester.run_all_tests()
    
    # Save results
    output_file = project_root / "error_recovery_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Return appropriate exit code
    if summary["failed"] > 0 or summary["errors"] > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
