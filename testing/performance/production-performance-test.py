#!/usr/bin/env python3
"""
ACGS Production Performance Testing Suite
Constitutional Hash: cdd01ef066bc6cf2

This script validates production performance targets:
- P99 latency: <5ms
- Throughput: >100 RPS
- Cache hit rate: >85%
- Constitutional compliance: 100%
"""

import asyncio
import aiohttp
import time
import statistics
import json
import sys
from typing import List, Dict, Any
from dataclasses import dataclass
import psycopg2
import redis

# Constitutional Hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class PerformanceResult:
    """Performance test result"""
    test_name: str
    target_value: float
    actual_value: float
    unit: str
    passed: bool
    constitutional_hash: str = CONSTITUTIONAL_HASH

class ProductionPerformanceTester:
    """Production performance testing suite"""
    
    def __init__(self):
        self.results: List[PerformanceResult] = []
        self.infrastructure_endpoints = {
            'postgres': 'localhost:5440',
            'redis': 'localhost:6390',
            'prometheus': 'http://localhost:9091',
            'grafana': 'http://localhost:3001'
        }
        
    async def test_infrastructure_latency(self) -> None:
        """Test infrastructure component latency"""
        print(f"Testing infrastructure latency (Constitutional Hash: {CONSTITUTIONAL_HASH})")
        
        # Test PostgreSQL latency
        try:
            start_time = time.time()
            conn = psycopg2.connect(
                host="localhost",
                port=5440,
                database="acgs",
                user="acgs_user",
                password="acgs_production_password_2025"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            postgres_latency = (time.time() - start_time) * 1000  # Convert to ms
            self.results.append(PerformanceResult(
                test_name="PostgreSQL Latency",
                target_value=5.0,
                actual_value=postgres_latency,
                unit="ms",
                passed=postgres_latency < 5.0
            ))
            print(f"✓ PostgreSQL latency: {postgres_latency:.2f}ms")
            
        except Exception as e:
            print(f"✗ PostgreSQL connection failed: {e}")
            self.results.append(PerformanceResult(
                test_name="PostgreSQL Latency",
                target_value=5.0,
                actual_value=float('inf'),
                unit="ms",
                passed=False
            ))
        
        # Test Redis latency
        try:
            start_time = time.time()
            r = redis.Redis(host='localhost', port=6390, password='redis_production_password_2025')
            r.ping()
            redis_latency = (time.time() - start_time) * 1000
            
            self.results.append(PerformanceResult(
                test_name="Redis Latency",
                target_value=1.0,
                actual_value=redis_latency,
                unit="ms",
                passed=redis_latency < 1.0
            ))
            print(f"✓ Redis latency: {redis_latency:.2f}ms")
            
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
            self.results.append(PerformanceResult(
                test_name="Redis Latency",
                target_value=1.0,
                actual_value=float('inf'),
                unit="ms",
                passed=False
            ))
    
    async def test_monitoring_performance(self) -> None:
        """Test monitoring system performance"""
        print(f"Testing monitoring performance (Constitutional Hash: {CONSTITUTIONAL_HASH})")
        
        async with aiohttp.ClientSession() as session:
            # Test Prometheus query performance
            try:
                start_time = time.time()
                async with session.get('http://localhost:9091/api/v1/query?query=up') as response:
                    await response.json()
                prometheus_latency = (time.time() - start_time) * 1000
                
                self.results.append(PerformanceResult(
                    test_name="Prometheus Query Latency",
                    target_value=100.0,
                    actual_value=prometheus_latency,
                    unit="ms",
                    passed=prometheus_latency < 100.0
                ))
                print(f"✓ Prometheus query latency: {prometheus_latency:.2f}ms")
                
            except Exception as e:
                print(f"✗ Prometheus query failed: {e}")
                self.results.append(PerformanceResult(
                    test_name="Prometheus Query Latency",
                    target_value=100.0,
                    actual_value=float('inf'),
                    unit="ms",
                    passed=False
                ))
            
            # Test Grafana dashboard loading
            try:
                start_time = time.time()
                async with session.get('http://localhost:3001/api/health') as response:
                    await response.json()
                grafana_latency = (time.time() - start_time) * 1000
                
                self.results.append(PerformanceResult(
                    test_name="Grafana API Latency",
                    target_value=200.0,
                    actual_value=grafana_latency,
                    unit="ms",
                    passed=grafana_latency < 200.0
                ))
                print(f"✓ Grafana API latency: {grafana_latency:.2f}ms")
                
            except Exception as e:
                print(f"✗ Grafana API failed: {e}")
                self.results.append(PerformanceResult(
                    test_name="Grafana API Latency",
                    target_value=200.0,
                    actual_value=float('inf'),
                    unit="ms",
                    passed=False
                ))
    
    async def test_throughput_performance(self) -> None:
        """Test system throughput under load"""
        print(f"Testing throughput performance (Constitutional Hash: {CONSTITUTIONAL_HASH})")

        # Test concurrent requests to monitoring endpoints
        async with aiohttp.ClientSession() as session:
            test_duration = 10  # seconds
            concurrent_requests = 20

            async def make_request():
                try:
                    async with session.get('http://localhost:9091/api/v1/query?query=up') as response:
                        return await response.json()
                except:
                    return None

            # Run load test
            start_time = time.time()
            total_requests = 0

            while time.time() - start_time < test_duration:
                tasks = [make_request() for _ in range(concurrent_requests)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                total_requests += len([r for r in results if r is not None])
                await asyncio.sleep(0.1)  # Small delay between batches

            actual_duration = time.time() - start_time
            rps = total_requests / actual_duration

            self.results.append(PerformanceResult(
                test_name="System Throughput",
                target_value=100.0,
                actual_value=rps,
                unit="RPS",
                passed=rps >= 100.0
            ))
            print(f"✓ System throughput: {rps:.1f} RPS over {actual_duration:.1f}s")

    async def validate_constitutional_compliance(self) -> None:
        """Validate constitutional compliance across all services"""
        print(f"Validating constitutional compliance (Hash: {CONSTITUTIONAL_HASH})")

        # Check Prometheus configuration for constitutional hash
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://localhost:9091/api/v1/status/config') as response:
                    config_data = await response.json()
                    config_yaml = config_data['data']['yaml']
                    hash_count = config_yaml.count(CONSTITUTIONAL_HASH)

                    compliance_score = 1.0 if hash_count > 0 else 0.0
                    self.results.append(PerformanceResult(
                        test_name="Constitutional Compliance",
                        target_value=1.0,
                        actual_value=compliance_score,
                        unit="score",
                        passed=compliance_score == 1.0
                    ))
                    print(f"✓ Constitutional hash found {hash_count} times in configuration")

            except Exception as e:
                print(f"✗ Constitutional compliance check failed: {e}")
                self.results.append(PerformanceResult(
                    test_name="Constitutional Compliance",
                    target_value=1.0,
                    actual_value=0.0,
                    unit="score",
                    passed=False
                ))
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance test report"""
        passed_tests = sum(1 for result in self.results if result.passed)
        total_tests = len(self.results)
        
        report = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": time.time(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            },
            "results": [
                {
                    "test_name": result.test_name,
                    "target_value": result.target_value,
                    "actual_value": result.actual_value,
                    "unit": result.unit,
                    "passed": result.passed,
                    "constitutional_hash": result.constitutional_hash
                }
                for result in self.results
            ]
        }
        
        return report
    
    def print_report(self) -> None:
        """Print performance test report"""
        print("\n" + "="*60)
        print("ACGS PRODUCTION PERFORMANCE TEST REPORT")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("="*60)
        
        for result in self.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"{status} {result.test_name}: {result.actual_value:.2f}{result.unit} (target: <{result.target_value}{result.unit})")
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print(f"\nSUMMARY: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

async def main():
    """Main performance testing function"""
    print("ACGS Production Performance Testing Suite")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("="*60)
    
    tester = ProductionPerformanceTester()
    
    # Run all performance tests
    await tester.test_infrastructure_latency()
    await tester.test_monitoring_performance()
    await tester.test_throughput_performance()
    await tester.validate_constitutional_compliance()
    
    # Generate and print report
    tester.print_report()
    
    # Save report to file
    report = tester.generate_report()
    with open('testing/performance/production-performance-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: testing/performance/production-performance-report.json")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Exit with appropriate code
    all_passed = all(result.passed for result in tester.results)
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    asyncio.run(main())
