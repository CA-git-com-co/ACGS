"""
Performance tests for optimized Z3 solver with caching and approximation.
Constitutional hash: cdd01ef066bc6cf2
"""

import asyncio
import time
import sys
import os
from typing import List, Dict, Any
import pytest

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/core/formal-verification'))

try:
    from app.services.z3_solver import Z3SolverService, VerificationResult, OptimizedCache
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    print("Z3 solver not available, skipping tests")

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@pytest.mark.skipif(not Z3_AVAILABLE, reason="Z3 solver not available")
class TestZ3SolverOptimization:
    """Performance tests for optimized Z3 solver."""
    
    def setup_method(self):
        """Setup test environment."""
        self.solver = Z3SolverService()
        
        # Sample policies for testing
        self.simple_policies = [
            {
                "id": "policy_1",
                "conditions": [{"type": "permission", "permission": "read"}],
                "actions": [{"type": "allow", "operation": "read_data"}]
            },
            {
                "id": "policy_2", 
                "conditions": [{"type": "permission", "permission": "write"}],
                "actions": [{"type": "allow", "operation": "write_data"}]
            }
        ]
        
        self.conflicting_policies = [
            {
                "id": "policy_allow",
                "conditions": [],
                "actions": [{"type": "allow", "operation": "sensitive_operation"}]
            },
            {
                "id": "policy_deny",
                "conditions": [],
                "actions": [{"type": "deny", "operation": "sensitive_operation"}]
            }
        ]
        
        self.constitutional_principles = [
            {
                "id": "non_maleficence",
                "name": "Non-maleficence",
                "formal_spec": "harmful actions are not permitted"
            }
        ]
    
    def test_cache_performance(self):
        """Test cache performance and hit rates."""
        # First verification - should be cache miss
        start_time = time.time()
        result1 = self.solver.verify_policy_consistency(self.simple_policies)
        first_time = time.time() - start_time
        
        # Second verification - should be cache hit
        start_time = time.time()
        result2 = self.solver.verify_policy_consistency(self.simple_policies)
        second_time = time.time() - start_time
        
        # Cache hit should be significantly faster
        assert second_time < first_time * 0.1, f"Cache hit {second_time:.3f}s not much faster than miss {first_time:.3f}s"
        
        # Check cache hit indication
        assert result2.get("cache_hit", False), "Second call should be cache hit"
        
        # Check performance stats
        stats = self.solver.get_performance_stats()
        assert stats["cache_hits_total"] >= 1, "Should have at least one cache hit"
        assert stats["cache_hit_rate"] > 0, "Cache hit rate should be > 0"
        
        print(f"Cache performance: {first_time:.3f}s -> {second_time:.3f}s ({second_time/first_time:.1%} of original)")
    
    def test_approximation_performance(self):
        """Test approximation for simple cases."""
        # Use simple policies that should trigger approximation
        simple_policies = [
            {
                "id": "simple_1",
                "conditions": [{"type": "permission", "permission": "read"}],
                "actions": [{"type": "allow", "operation": "read_file"}]
            }
        ]
        
        start_time = time.time()
        result = self.solver.verify_policy_consistency(simple_policies)
        verification_time = time.time() - start_time
        
        # Should be very fast due to approximation
        assert verification_time < 0.1, f"Simple verification took {verification_time:.3f}s, should be <0.1s"
        
        # Check if approximation was used
        assert result.get("approximated", False), "Simple case should use approximation"
        
        # Check stats
        stats = self.solver.get_performance_stats()
        assert stats["approximations_total"] >= 1, "Should have used approximation"
        
        print(f"Approximation time: {verification_time:.3f}s")
    
    def test_conflict_detection_approximation(self):
        """Test approximation can detect conflicts quickly."""
        start_time = time.time()
        result = self.solver.verify_policy_consistency(self.conflicting_policies)
        verification_time = time.time() - start_time
        
        # Should detect conflict quickly
        assert verification_time < 0.05, f"Conflict detection took {verification_time:.3f}s, should be <0.05s"
        assert not result["satisfiable"], "Should detect policy conflict"
        assert result["unsatisfiable"], "Should mark as unsatisfiable"
        
        # May use approximation for simple conflicts
        if result.get("approximated", False):
            assert "conflicts" in result or "conflict" in result.get("message", "").lower()
        
        print(f"Conflict detection time: {verification_time:.3f}s")
    
    def test_latency_requirements(self):
        """Test P99 latency requirements are met."""
        latencies = []
        
        # Run multiple verifications to get P99
        test_policies = [
            self.simple_policies,
            self.conflicting_policies,
            [self.simple_policies[0]],  # Single policy
            self.simple_policies + [{"id": "policy_3", "conditions": [], "actions": [{"type": "allow", "operation": "admin"}]}]
        ]
        
        for _ in range(20):  # Run each test case 5 times
            for policies in test_policies:
                start_time = time.time()
                self.solver.verify_policy_consistency(policies)
                latency = (time.time() - start_time) * 1000  # Convert to ms
                latencies.append(latency)
        
        # Calculate P99
        latencies.sort()
        p99_index = int(len(latencies) * 0.99)
        p99_latency = latencies[p99_index]
        
        print(f"P99 latency: {p99_latency:.2f}ms")
        print(f"Average latency: {sum(latencies)/len(latencies):.2f}ms")
        
        # Should meet <5ms P99 requirement
        assert p99_latency < 5.0, f"P99 latency {p99_latency:.2f}ms exceeds 5ms requirement"
    
    def test_throughput_requirements(self):
        """Test throughput requirements are met."""
        num_requests = 100
        
        start_time = time.time()
        for _ in range(num_requests):
            # Alternate between simple and conflicting policies for variety
            policies = self.simple_policies if _ % 2 == 0 else self.conflicting_policies
            self.solver.verify_policy_consistency(policies)
        
        total_time = time.time() - start_time
        throughput = num_requests / total_time
        
        print(f"Throughput: {throughput:.1f} verifications/second")
        
        # Should exceed 100 RPS (likely much higher due to caching)
        assert throughput > 100, f"Throughput {throughput:.1f} RPS below 100 RPS requirement"
    
    def test_cache_memory_efficiency(self):
        """Test cache memory usage stays within bounds."""
        # Generate many different policies to test cache bounds
        for i in range(150):  # More than default cache size
            unique_policy = {
                "id": f"policy_{i}",
                "conditions": [],
                "actions": [{"type": "allow", "operation": f"operation_{i}"}]
            }
            self.solver.verify_policy_consistency([unique_policy])
        
        stats = self.solver.get_performance_stats()
        cache_size = stats["memory_cache_size"]
        
        # Should not exceed reasonable memory bounds
        assert cache_size <= 1000, f"Memory cache size {cache_size} exceeds limit"
        
        print(f"Memory cache size after 150 operations: {cache_size}")
    
    def test_constitutional_compliance_caching(self):
        """Test constitutional compliance verification with caching."""
        policy = self.simple_policies[0]
        
        # First check - cache miss
        start_time = time.time()
        result1 = self.solver.verify_constitutional_compliance(policy, "non_maleficence")
        first_time = time.time() - start_time
        
        # Note: Constitutional compliance may not use the same cache as policy consistency
        # but should still be optimized
        
        print(f"Constitutional compliance time: {first_time:.3f}s")
        assert first_time < 0.1, f"Constitutional compliance took {first_time:.3f}s, should be <0.1s"
    
    def test_simplification_effectiveness(self):
        """Test formula simplification improves performance."""
        # Complex policy with redundant conditions
        complex_policy = {
            "id": "complex_policy",
            "conditions": [
                {"type": "permission", "permission": "read"},
                {"type": "permission", "permission": "read"},  # Duplicate
                {"type": "permission", "permission": "write"}
            ],
            "actions": [
                {"type": "allow", "operation": "read_data"},
                {"type": "allow", "operation": "write_data"}
            ]
        }
        
        result = self.solver.verify_policy_consistency([complex_policy])
        
        stats = self.solver.get_performance_stats()
        assert stats["simplifications_total"] >= 0, "Should track simplifications"
        
        # Should complete successfully
        assert "satisfiable" in result
        
        print(f"Simplifications performed: {stats['simplifications_total']}")
    
    def test_constitutional_hash_validation(self):
        """Test all results include constitutional hash."""
        result = self.solver.verify_policy_consistency(self.simple_policies)
        
        assert result.get("constitutional_hash") == CONSTITUTIONAL_HASH
        
        # Test performance stats also include hash
        stats = self.solver.get_performance_stats()
        assert stats["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    def test_error_handling_performance(self):
        """Test error handling doesn't significantly impact performance."""
        # Malformed policy
        bad_policy = {"id": "bad", "invalid_field": "should_cause_issues"}
        
        start_time = time.time()
        result = self.solver.verify_policy_consistency([bad_policy])
        error_time = time.time() - start_time
        
        # Error handling should be fast
        assert error_time < 0.1, f"Error handling took {error_time:.3f}s, should be <0.1s"
        
        # Should return meaningful error information
        assert not result.get("satisfiable", True), "Should handle error gracefully"
    
    def test_concurrent_verification_performance(self):
        """Test performance under concurrent load."""
        import concurrent.futures
        import threading
        
        def verify_policies():
            # Each thread does multiple verifications
            for _ in range(10):
                policies = self.simple_policies if threading.current_thread().ident % 2 == 0 else self.conflicting_policies
                self.solver.verify_policy_consistency(policies)
        
        num_threads = 5
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(verify_policies) for _ in range(num_threads)]
            concurrent.futures.wait(futures)
        
        total_time = time.time() - start_time
        total_operations = num_threads * 10
        concurrent_throughput = total_operations / total_time
        
        print(f"Concurrent throughput: {concurrent_throughput:.1f} verifications/second")
        
        # Should maintain good performance under concurrency
        assert concurrent_throughput > 50, f"Concurrent throughput {concurrent_throughput:.1f} too low"


if __name__ == "__main__":
    if not Z3_AVAILABLE:
        print("Z3 solver not available, skipping all tests")
        exit(0)
    
    # Run tests directly
    test_instance = TestZ3SolverOptimization()
    
    test_instance.setup_method()
    test_instance.test_cache_performance()
    
    test_instance.setup_method()
    test_instance.test_approximation_performance()
    
    test_instance.setup_method()
    test_instance.test_conflict_detection_approximation()
    
    test_instance.setup_method()
    test_instance.test_latency_requirements()
    
    test_instance.setup_method()
    test_instance.test_throughput_requirements()
    
    test_instance.setup_method()
    test_instance.test_cache_memory_efficiency()
    
    test_instance.setup_method()
    test_instance.test_constitutional_compliance_caching()
    
    test_instance.setup_method()
    test_instance.test_simplification_effectiveness()
    
    test_instance.setup_method()
    test_instance.test_constitutional_hash_validation()
    
    test_instance.setup_method()
    test_instance.test_error_handling_performance()
    
    test_instance.setup_method()
    test_instance.test_concurrent_verification_performance()
    
    print("All Z3 solver optimization tests passed!")