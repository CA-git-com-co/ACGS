#!/usr/bin/env python3
# Load Testing Script for Critical Paths - 5ms P99 Target
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import time
import json
import statistics
from typing import Dict, List, Any
import httpx
import redis.asyncio as aioredis
import asyncpg
import os

# Configuration
LOAD_TEST_CONFIG = {
    "concurrent_users": 100,
    "requests_per_user": 50,
    "test_duration": 60,  # seconds
    "target_p99_latency": 5.0,  # ms
    "target_throughput": 1000,  # RPS
}

class LoadTester:
    def __init__(self):
        self.results = {}
        self.redis_client = None
        self.db_pool = None
        self.http_client = None
        
    async def initialize(self):
        """Initialize connections for load testing"""
        # Redis connection
        self.redis_client = aioredis.from_url(
            "redis://localhost:6389/0",
            max_connections=200,
            decode_responses=True
        )
        
        # PostgreSQL connection pool
        self.db_pool = await asyncpg.create_pool(
            host="localhost",
            port=5439,
            user="acgs_user",
            password=os.environ.get("POSTGRES_PASSWORD", "acgs_password"),
            database="acgs_db",
            min_size=20,
            max_size=100,
            command_timeout=10
        )
        
        # HTTP client for API testing
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=200, max_keepalive_connections=100)
        )
    
    async def test_redis_load(self, user_id: int, requests: int) -> List[float]:
        """Test Redis under load"""
        latencies = []
        
        for i in range(requests):
            key = f"load_test_user_{user_id}_req_{i}"
            value = {"user_id": user_id, "request_id": i, "timestamp": time.time()}
            
            # SET operation
            start = time.perf_counter()
            await self.redis_client.set(key, json.dumps(value), ex=300)
            latencies.append((time.perf_counter() - start) * 1000)
            
            # GET operation
            start = time.perf_counter()
            await self.redis_client.get(key)
            latencies.append((time.perf_counter() - start) * 1000)
        
        return latencies
    
    async def test_database_load(self, user_id: int, requests: int) -> List[float]:
        """Test database under load"""
        latencies = []
        
        async with self.db_pool.acquire() as conn:
            for i in range(requests):
                agent_id = f"load_test_agent_{user_id}_{i}"
                
                # INSERT operation
                start = time.perf_counter()
                await conn.execute("""
                    INSERT INTO agent_confidence_profiles 
                    (agent_id, operation_confidence_adjustments, metadata) 
                    VALUES ($1, $2, $3)
                    ON CONFLICT (agent_id) DO UPDATE SET updated_at = NOW()
                """, agent_id, "{}", '{"load_test": true}')
                latencies.append((time.perf_counter() - start) * 1000)
                
                # SELECT operation
                start = time.perf_counter()
                await conn.fetchrow(
                    "SELECT * FROM agent_confidence_profiles WHERE agent_id = $1",
                    agent_id
                )
                latencies.append((time.perf_counter() - start) * 1000)
        
        return latencies
    
    async def test_api_load(self, user_id: int, requests: int) -> List[float]:
        """Test API endpoints under load"""
        latencies = []
        
        for i in range(requests):
            try:
                # Test health endpoint
                start = time.perf_counter()
                response = await self.http_client.get("http://localhost:8080/health")
                latencies.append((time.perf_counter() - start) * 1000)
                
                if response.status_code != 200:
                    print(f"API request failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"API request failed: {e}")
                latencies.append(10000)  # 10 second penalty for failed requests
        
        return latencies
    
    async def run_concurrent_load_test(self, test_func, test_name: str) -> Dict[str, Any]:
        """Run concurrent load test"""
        print(f"🚀 Starting {test_name} load test...")
        print(f"  Concurrent users: {LOAD_TEST_CONFIG['concurrent_users']}")
        print(f"  Requests per user: {LOAD_TEST_CONFIG['requests_per_user']}")
        
        start_time = time.perf_counter()
        
        # Create concurrent tasks
        tasks = []
        for user_id in range(LOAD_TEST_CONFIG['concurrent_users']):
            task = asyncio.create_task(
                test_func(user_id, LOAD_TEST_CONFIG['requests_per_user'])
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        all_latencies = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.perf_counter() - start_time
        
        # Flatten latencies and filter out exceptions
        flat_latencies = []
        for user_latencies in all_latencies:
            if isinstance(user_latencies, list):
                flat_latencies.extend(user_latencies)
            else:
                print(f"Task failed: {user_latencies}")
        
        if not flat_latencies:
            return {"error": "No successful requests"}
        
        # Calculate metrics
        total_requests = len(flat_latencies)
        throughput = total_requests / total_time
        
        return {
            "total_requests": total_requests,
            "total_time_seconds": total_time,
            "throughput_rps": throughput,
            "latency_stats": {
                "min": min(flat_latencies),
                "max": max(flat_latencies),
                "avg": statistics.mean(flat_latencies),
                "p50": statistics.quantiles(flat_latencies, n=2)[0],
                "p95": statistics.quantiles(flat_latencies, n=20)[18],
                "p99": statistics.quantiles(flat_latencies, n=100)[98],
            },
            "target_compliance": {
                "p99_meets_target": statistics.quantiles(flat_latencies, n=100)[98] < LOAD_TEST_CONFIG['target_p99_latency'],
                "throughput_meets_target": throughput >= LOAD_TEST_CONFIG['target_throughput']
            }
        }
    
    async def run_full_load_test(self):
        """Run comprehensive load test"""
        print("🔥 Starting comprehensive load test...")
        print(f"Target P99 latency: {LOAD_TEST_CONFIG['target_p99_latency']} ms")
        print(f"Target throughput: {LOAD_TEST_CONFIG['target_throughput']} RPS")
        
        await self.initialize()
        
        # Run load tests
        self.results["redis_load"] = await self.run_concurrent_load_test(
            self.test_redis_load, "Redis"
        )
        
        self.results["database_load"] = await self.run_concurrent_load_test(
            self.test_database_load, "Database"
        )
        
        # Note: API load test would require API to be running
        # self.results["api_load"] = await self.run_concurrent_load_test(
        #     self.test_api_load, "API"
        # )
        
        # Generate report
        await self.generate_load_test_report()
        
        # Cleanup
        await self.cleanup()
    
    async def generate_load_test_report(self):
        """Generate comprehensive load test report"""
        print("\n" + "="*80)
        print("LOAD TEST REPORT - CRITICAL PATHS")
        print("Constitutional Hash: cdd01ef066bc6cf2")
        print("="*80)
        
        for test_name, results in self.results.items():
            if "error" in results:
                print(f"\n❌ {test_name.upper()} FAILED: {results['error']}")
                continue
                
            latency_stats = results["latency_stats"]
            compliance = results["target_compliance"]
            
            print(f"\n📊 {test_name.upper()} RESULTS:")
            print(f"  Total Requests: {results['total_requests']:,}")
            print(f"  Total Time: {results['total_time_seconds']:.2f} seconds")
            print(f"  Throughput: {results['throughput_rps']:.2f} RPS")
            print(f"  Latency Stats:")
            print(f"    Min: {latency_stats['min']:.2f} ms")
            print(f"    Avg: {latency_stats['avg']:.2f} ms")
            print(f"    P50: {latency_stats['p50']:.2f} ms")
            print(f"    P95: {latency_stats['p95']:.2f} ms")
            print(f"    P99: {latency_stats['p99']:.2f} ms")
            print(f"    Max: {latency_stats['max']:.2f} ms")
            
            # Target compliance
            p99_status = "✅" if compliance["p99_meets_target"] else "❌"
            throughput_status = "✅" if compliance["throughput_meets_target"] else "❌"
            
            print(f"  Target Compliance:")
            print(f"    {p99_status} P99 < {LOAD_TEST_CONFIG['target_p99_latency']} ms: {compliance['p99_meets_target']}")
            print(f"    {throughput_status} Throughput >= {LOAD_TEST_CONFIG['target_throughput']} RPS: {compliance['throughput_meets_target']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        all_compliant = all(
            results.get("target_compliance", {}).get("p99_meets_target", False) and
            results.get("target_compliance", {}).get("throughput_meets_target", False)
            for results in self.results.values()
            if "error" not in results
        )
        
        if all_compliant:
            print("✅ All critical paths meet performance targets!")
        else:
            print("❌ Some critical paths do not meet performance targets")
            print("🔧 Recommendations:")
            print("  - Review connection pool configurations")
            print("  - Optimize database queries")
            print("  - Consider Redis cluster setup")
            print("  - Implement caching strategies")
        
        # Save results to file
        with open("/home/dislove/ACGS-2/load_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📁 Results saved to: load_test_results.json")
    
    async def cleanup(self):
        """Clean up connections and test data"""
        if self.redis_client:
            # Clean up Redis test data
            keys = await self.redis_client.keys("load_test_*")
            if keys:
                await self.redis_client.delete(*keys)
            await self.redis_client.close()
        
        if self.db_pool:
            # Clean up database test data
            async with self.db_pool.acquire() as conn:
                await conn.execute("DELETE FROM agent_confidence_profiles WHERE agent_id LIKE 'load_test_agent_%'")
            await self.db_pool.close()
        
        if self.http_client:
            await self.http_client.aclose()

async def main():
    tester = LoadTester()
    await tester.run_full_load_test()

if __name__ == "__main__":
    asyncio.run(main())
