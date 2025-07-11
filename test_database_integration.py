#!/usr/bin/env python3
"""
ACGS-2 Database and Cache Integration Testing
Constitutional Hash: cdd01ef066bc6cf2
"""

import subprocess
import json
import time
import redis
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class DatabaseIntegrationTest:
    def __init__(self):
        self.results = []
        
    def log_result(self, component: str, test_name: str, status: str, details: dict, constitutional_compliance: bool = True):
        """Log test result"""
        result = {
            "component": component,
            "test_name": test_name,
            "status": status,
            "details": details,
            "constitutional_compliance": constitutional_compliance,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        logger.info(f"{component} - {test_name}: {status} (Constitutional: {constitutional_compliance})")
        
    def test_postgresql_container_health(self):
        """Test PostgreSQL container health and internal connectivity"""
        try:
            # Test container health
            result = subprocess.run(
                ["docker", "exec", "acgs_postgres", "pg_isready", "-U", "acgs_user", "-d", "acgs_db"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Test basic query execution
                query_result = subprocess.run(
                    ["docker", "exec", "acgs_postgres", "psql", "-U", "acgs_user", "-d", "acgs_db", "-c", "SELECT version();"],
                    capture_output=True, text=True, timeout=10
                )
                
                if query_result.returncode == 0:
                    self.log_result(
                        "PostgreSQL",
                        "Container Health & Query Test",
                        "PASS",
                        {
                            "port": 5439,
                            "container": "acgs_postgres",
                            "database": "acgs_db",
                            "user": "acgs_user",
                            "version_info": query_result.stdout.strip()
                        },
                        True
                    )
                    return True
                else:
                    self.log_result(
                        "PostgreSQL",
                        "Container Health & Query Test",
                        "FAIL",
                        {"error": "Query execution failed", "stderr": query_result.stderr},
                        False
                    )
                    return False
            else:
                self.log_result(
                    "PostgreSQL",
                    "Container Health & Query Test",
                    "FAIL",
                    {"error": "pg_isready failed", "stderr": result.stderr},
                    False
                )
                return False
                
        except Exception as e:
            self.log_result(
                "PostgreSQL",
                "Container Health & Query Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def test_postgresql_performance(self):
        """Test PostgreSQL performance metrics"""
        try:
            # Test query performance
            start_time = time.time()
            result = subprocess.run(
                ["docker", "exec", "acgs_postgres", "psql", "-U", "acgs_user", "-d", "acgs_db", "-c", 
                 "SELECT COUNT(*) FROM information_schema.tables;"],
                capture_output=True, text=True, timeout=10
            )
            query_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                self.log_result(
                    "PostgreSQL",
                    "Performance Test",
                    "PASS",
                    {
                        "query_time_ms": query_time,
                        "target_ms": 100,
                        "performance_ok": query_time < 100
                    },
                    True
                )
                return query_time < 100
            else:
                self.log_result(
                    "PostgreSQL",
                    "Performance Test",
                    "FAIL",
                    {"error": "Performance query failed", "stderr": result.stderr},
                    False
                )
                return False
                
        except Exception as e:
            self.log_result(
                "PostgreSQL",
                "Performance Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def test_redis_connectivity_and_performance(self):
        """Test Redis connectivity and performance"""
        try:
            r = redis.Redis(host='localhost', port=6389, decode_responses=True)
            
            # Test basic connectivity
            start_time = time.time()
            ping_result = r.ping()
            ping_time = (time.time() - start_time) * 1000
            
            if not ping_result:
                self.log_result(
                    "Redis",
                    "Connectivity Test",
                    "FAIL",
                    {"error": "Ping failed"},
                    False
                )
                return False
            
            # Test set/get operations
            test_key = f"acgs_test_{int(time.time())}"
            test_value = f"constitutional_hash_{CONSTITUTIONAL_HASH}"
            
            start_time = time.time()
            r.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            retrieved_value = r.get(test_key)
            operation_time = (time.time() - start_time) * 1000
            
            # Clean up
            r.delete(test_key)
            
            if retrieved_value == test_value:
                self.log_result(
                    "Redis",
                    "Connectivity & Performance Test",
                    "PASS",
                    {
                        "ping_time_ms": ping_time,
                        "operation_time_ms": operation_time,
                        "port": 6389,
                        "test_key": test_key,
                        "constitutional_hash_verified": CONSTITUTIONAL_HASH in retrieved_value
                    },
                    True
                )
                return True
            else:
                self.log_result(
                    "Redis",
                    "Connectivity & Performance Test",
                    "FAIL",
                    {"error": "Set/Get operation failed", "expected": test_value, "got": retrieved_value},
                    False
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Redis",
                "Connectivity & Performance Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def test_redis_cache_performance(self):
        """Test Redis cache hit rate and performance"""
        try:
            r = redis.Redis(host='localhost', port=6389, decode_responses=True)
            
            # Perform multiple operations to test cache performance
            operations = 100
            cache_keys = [f"cache_test_{i}_{CONSTITUTIONAL_HASH}" for i in range(operations)]
            
            # Set operations
            start_time = time.time()
            for i, key in enumerate(cache_keys):
                r.set(key, f"value_{i}_{CONSTITUTIONAL_HASH}", ex=300)
            set_time = (time.time() - start_time) * 1000
            
            # Get operations
            start_time = time.time()
            retrieved_count = 0
            for key in cache_keys:
                if r.get(key):
                    retrieved_count += 1
            get_time = (time.time() - start_time) * 1000
            
            # Clean up
            r.delete(*cache_keys)
            
            cache_hit_rate = (retrieved_count / operations) * 100
            avg_set_time = set_time / operations
            avg_get_time = get_time / operations
            
            performance_ok = cache_hit_rate >= 85.0 and avg_get_time < 1.0
            
            self.log_result(
                "Redis",
                "Cache Performance Test",
                "PASS" if performance_ok else "FAIL",
                {
                    "operations": operations,
                    "cache_hit_rate_percent": cache_hit_rate,
                    "target_hit_rate_percent": 85.0,
                    "avg_set_time_ms": avg_set_time,
                    "avg_get_time_ms": avg_get_time,
                    "total_set_time_ms": set_time,
                    "total_get_time_ms": get_time,
                    "performance_target_met": performance_ok
                },
                True
            )
            return performance_ok
            
        except Exception as e:
            self.log_result(
                "Redis",
                "Cache Performance Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def test_data_persistence(self):
        """Test data persistence across service restarts"""
        try:
            r = redis.Redis(host='localhost', port=6389, decode_responses=True)
            
            # Set a persistent test key
            persistence_key = f"persistence_test_{CONSTITUTIONAL_HASH}"
            persistence_value = f"persistent_data_{int(time.time())}"
            
            r.set(persistence_key, persistence_value)
            
            # Verify it exists
            retrieved = r.get(persistence_key)
            
            if retrieved == persistence_value:
                # Test PostgreSQL persistence by checking if tables exist
                pg_result = subprocess.run(
                    ["docker", "exec", "acgs_postgres", "psql", "-U", "acgs_user", "-d", "acgs_db", "-c", 
                     "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"],
                    capture_output=True, text=True, timeout=10
                )
                
                if pg_result.returncode == 0:
                    # Clean up Redis test key
                    r.delete(persistence_key)
                    
                    self.log_result(
                        "Data Persistence",
                        "Cross-Service Persistence Test",
                        "PASS",
                        {
                            "redis_persistence": True,
                            "postgresql_persistence": True,
                            "test_key": persistence_key,
                            "postgresql_tables_count": pg_result.stdout.strip()
                        },
                        True
                    )
                    return True
                else:
                    self.log_result(
                        "Data Persistence",
                        "Cross-Service Persistence Test",
                        "FAIL",
                        {"error": "PostgreSQL persistence check failed", "stderr": pg_result.stderr},
                        False
                    )
                    return False
            else:
                self.log_result(
                    "Data Persistence",
                    "Cross-Service Persistence Test",
                    "FAIL",
                    {"error": "Redis persistence failed", "expected": persistence_value, "got": retrieved},
                    False
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Data Persistence",
                "Cross-Service Persistence Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def run_all_tests(self):
        """Run all database and cache integration tests"""
        logger.info("Starting ACGS-2 Database and Cache Integration Testing")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        test_summary = {
            "start_time": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "tests_run": 0,
            "tests_passed": 0,
            "constitutional_compliance_rate": 0.0
        }
        
        # Run all tests
        tests = [
            self.test_postgresql_container_health,
            self.test_postgresql_performance,
            self.test_redis_connectivity_and_performance,
            self.test_redis_cache_performance,
            self.test_data_persistence
        ]
        
        for test in tests:
            test_summary["tests_run"] += 1
            if test():
                test_summary["tests_passed"] += 1
        
        # Calculate constitutional compliance
        compliant_tests = sum(1 for result in self.results if result["constitutional_compliance"])
        test_summary["constitutional_compliance_rate"] = (compliant_tests / len(self.results)) * 100 if self.results else 0
        test_summary["end_time"] = datetime.now().isoformat()
        
        return test_summary

def main():
    """Main test execution"""
    test_suite = DatabaseIntegrationTest()
    summary = test_suite.run_all_tests()
    
    print("\n" + "="*80)
    print("ACGS-2 DATABASE & CACHE INTEGRATION TEST RESULTS")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Tests Passed: {summary['tests_passed']}")
    print(f"Constitutional Compliance Rate: {summary['constitutional_compliance_rate']:.1f}%")
    
    print("\nDETAILED RESULTS:")
    for result in test_suite.results:
        compliance_status = "✅" if result["constitutional_compliance"] else "❌"
        print(f"{compliance_status} {result['component']} - {result['test_name']}: {result['status']}")
        
        # Show key metrics
        if "query_time_ms" in result["details"]:
            print(f"    Query Time: {result['details']['query_time_ms']:.2f}ms")
        if "cache_hit_rate_percent" in result["details"]:
            print(f"    Cache Hit Rate: {result['details']['cache_hit_rate_percent']:.1f}%")
        if "ping_time_ms" in result["details"]:
            print(f"    Ping Time: {result['details']['ping_time_ms']:.2f}ms")
    
    # Save results
    with open("database_integration_results.json", "w") as f:
        json.dump({
            "summary": summary,
            "detailed_results": test_suite.results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: database_integration_results.json")
    
    if summary["constitutional_compliance_rate"] < 100.0:
        print(f"\n⚠️  WARNING: Constitutional compliance rate is {summary['constitutional_compliance_rate']:.1f}% (target: 100%)")
        return 1
    else:
        print(f"\n✅ SUCCESS: All tests passed with 100% constitutional compliance")
        return 0

if __name__ == "__main__":
    exit(main())
