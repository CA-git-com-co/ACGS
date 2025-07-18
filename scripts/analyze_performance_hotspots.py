#!/usr/bin/env python3
# Performance Hotspot Analysis Script
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import time
import json
import statistics
from typing import Dict, List, Any
import redis.asyncio as aioredis
import asyncpg
import os

# Target performance metrics
TARGET_P99_LATENCY = 5.0  # 5 ms P99 latency target

class PerformanceAnalyzer:
    def __init__(self):
        self.results = {}
        self.redis_client = None
        self.db_conn = None
        
    async def initialize_connections(self):
        """Initialize Redis and PostgreSQL connections"""
        # Redis connection
        self.redis_client = aioredis.from_url(
            "redis://localhost:6389/0",
            max_connections=50,
            decode_responses=True
        )
        
        # PostgreSQL connection
        self.db_conn = await asyncpg.connect(
            host="localhost",
            port=5439,
            user="acgs_user",
            password=os.environ.get("POSTGRES_PASSWORD", "acgs_password"),
            database="acgs_db"
        )
    
    async def analyze_redis_cache_performance(self) -> Dict[str, Any]:
        """Analyze Redis cache performance and identify hotspots"""
        print("🔍 Analyzing Redis cache performance...")
        
        # Test cache hit/miss patterns
        cache_operations = []
        
        # Simulate cache operations
        for i in range(500):
            key = f"hotspot_test_{i}"
            value = {"data": f"test_value_{i}", "timestamp": time.time()}
            
            # SET operation
            start = time.perf_counter()
            await self.redis_client.set(key, json.dumps(value), ex=300)
            set_time = (time.perf_counter() - start) * 1000
            
            # GET operation
            start = time.perf_counter()
            result = await self.redis_client.get(key)
            get_time = (time.perf_counter() - start) * 1000
            
            cache_operations.append({
                "set_time_ms": set_time,
                "get_time_ms": get_time,
                "cache_hit": result is not None
            })
        
        # Test connection pool stress
        pool_stress_times = []
        for _ in range(100):
            start = time.perf_counter()
            await self.redis_client.ping()
            pool_stress_times.append((time.perf_counter() - start) * 1000)
        
        # Calculate metrics
        set_times = [op["set_time_ms"] for op in cache_operations]
        get_times = [op["get_time_ms"] for op in cache_operations]
        cache_hit_rate = sum(1 for op in cache_operations if op["cache_hit"]) / len(cache_operations)
        
        return {
            "cache_hit_rate": cache_hit_rate,
            "set_latency": {
                "avg": statistics.mean(set_times),
                "p95": statistics.quantiles(set_times, n=20)[18],
                "p99": statistics.quantiles(set_times, n=100)[98],
                "max": max(set_times)
            },
            "get_latency": {
                "avg": statistics.mean(get_times),
                "p95": statistics.quantiles(get_times, n=20)[18],
                "p99": statistics.quantiles(get_times, n=100)[98],
                "max": max(get_times)
            },
            "pool_stress": {
                "avg": statistics.mean(pool_stress_times),
                "p95": statistics.quantiles(pool_stress_times, n=20)[18],
                "p99": statistics.quantiles(pool_stress_times, n=100)[98],
                "max": max(pool_stress_times)
            }
        }
    
    async def analyze_database_performance(self) -> Dict[str, Any]:
        """Analyze database performance and identify N+1 query risks"""
        print("🗄️ Analyzing database performance...")
        
        # Test connection pool performance
        connection_times = []
        for _ in range(50):
            start = time.perf_counter()
            await self.db_conn.fetchval("SELECT 1")
            connection_times.append((time.perf_counter() - start) * 1000)
        
        # Test complex query performance
        complex_query_times = []
        for i in range(20):
            start = time.perf_counter()
            await self.db_conn.fetch("""
                SELECT ac.agent_id, ac.operation_confidence_adjustments, 
                       rf.feedback_type, rf.feedback_score
                FROM agent_confidence_profiles ac
                LEFT JOIN review_feedbacks rf ON ac.agent_id = rf.agent_id
                WHERE ac.created_at > NOW() - INTERVAL '1 day'
                LIMIT 100
            """)
            complex_query_times.append((time.perf_counter() - start) * 1000)
        
        # Simulate N+1 query pattern (bad practice)
        n_plus_one_times = []
        agent_ids = [f"test_agent_{i}" for i in range(10)]
        
        # Create test data
        for agent_id in agent_ids:
            await self.db_conn.execute("""
                INSERT INTO agent_confidence_profiles 
                (agent_id, operation_confidence_adjustments, metadata) 
                VALUES ($1, $2, $3)
                ON CONFLICT (agent_id) DO UPDATE SET updated_at = NOW()
            """, agent_id, "{}", '{"test": true}')
        
        # N+1 query pattern
        start = time.perf_counter()
        agents = await self.db_conn.fetch("SELECT agent_id FROM agent_confidence_profiles WHERE agent_id LIKE 'test_agent_%'")
        for agent in agents:
            await self.db_conn.fetchrow(
                "SELECT * FROM agent_confidence_profiles WHERE agent_id = $1",
                agent["agent_id"]
            )
        n_plus_one_time = (time.perf_counter() - start) * 1000
        
        # Better approach - single query
        start = time.perf_counter()
        await self.db_conn.fetch("""
            SELECT * FROM agent_confidence_profiles 
            WHERE agent_id = ANY($1)
        """, agent_ids)
        optimized_time = (time.perf_counter() - start) * 1000
        
        # Cleanup
        await self.db_conn.execute("DELETE FROM agent_confidence_profiles WHERE agent_id LIKE 'test_agent_%'")
        
        return {
            "connection_pool": {
                "avg": statistics.mean(connection_times),
                "p95": statistics.quantiles(connection_times, n=20)[18],
                "p99": statistics.quantiles(connection_times, n=100)[98],
                "max": max(connection_times)
            },
            "complex_queries": {
                "avg": statistics.mean(complex_query_times),
                "p95": statistics.quantiles(complex_query_times, n=20)[18] if len(complex_query_times) > 20 else max(complex_query_times),
                "p99": statistics.quantiles(complex_query_times, n=100)[98] if len(complex_query_times) > 100 else max(complex_query_times),
                "max": max(complex_query_times)
            },
            "n_plus_one_comparison": {
                "n_plus_one_time_ms": n_plus_one_time,
                "optimized_time_ms": optimized_time,
                "improvement_factor": n_plus_one_time / optimized_time if optimized_time > 0 else 0
            }
        }
    
    async def analyze_cpu_intensive_tasks(self) -> Dict[str, Any]:
        """Analyze CPU-intensive operations"""
        print("🚀 Analyzing CPU-intensive tasks...")
        
        # JSON serialization/deserialization
        json_times = []
        large_data = {"key_" + str(i): f"value_{i}" * 100 for i in range(1000)}
        
        for _ in range(100):
            start = time.perf_counter()
            serialized = json.dumps(large_data)
            json.loads(serialized)
            json_times.append((time.perf_counter() - start) * 1000)
        
        # String operations
        string_times = []
        for _ in range(1000):
            start = time.perf_counter()
            result = "test_string_" + str(time.time())
            result.upper().lower().replace("_", "-")
            string_times.append((time.perf_counter() - start) * 1000)
        
        return {
            "json_operations": {
                "avg": statistics.mean(json_times),
                "p95": statistics.quantiles(json_times, n=20)[18],
                "p99": statistics.quantiles(json_times, n=100)[98],
                "max": max(json_times)
            },
            "string_operations": {
                "avg": statistics.mean(string_times),
                "p95": statistics.quantiles(string_times, n=20)[18],
                "p99": statistics.quantiles(string_times, n=100)[98],
                "max": max(string_times)
            }
        }
    
    async def run_full_analysis(self):
        """Run comprehensive performance analysis"""
        print("🔍 Starting comprehensive performance analysis...")
        
        await self.initialize_connections()
        
        # Run all analyses
        self.results["redis_cache"] = await self.analyze_redis_cache_performance()
        self.results["database"] = await self.analyze_database_performance()
        self.results["cpu_intensive"] = await self.analyze_cpu_intensive_tasks()
        
        # Generate report
        await self.generate_performance_report()
        
        # Cleanup
        await self.cleanup()
    
    async def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "="*80)
        print("PERFORMANCE HOTSPOT ANALYSIS REPORT")
        print("Constitutional Hash: cdd01ef066bc6cf2")
        print("="*80)
        
        # Redis analysis
        redis_results = self.results["redis_cache"]
        print(f"\n🔴 REDIS CACHE ANALYSIS:")
        print(f"  Cache Hit Rate: {redis_results['cache_hit_rate']:.2%}")
        print(f"  SET P99 Latency: {redis_results['set_latency']['p99']:.2f} ms")
        print(f"  GET P99 Latency: {redis_results['get_latency']['p99']:.2f} ms")
        print(f"  Pool Stress P99: {redis_results['pool_stress']['p99']:.2f} ms")
        
        # Database analysis
        db_results = self.results["database"]
        print(f"\n🗄️ DATABASE ANALYSIS:")
        print(f"  Connection Pool P99: {db_results['connection_pool']['p99']:.2f} ms")
        print(f"  Complex Query P99: {db_results['complex_queries']['p99']:.2f} ms")
        print(f"  N+1 Query Time: {db_results['n_plus_one_comparison']['n_plus_one_time_ms']:.2f} ms")
        print(f"  Optimized Query Time: {db_results['n_plus_one_comparison']['optimized_time_ms']:.2f} ms")
        print(f"  Improvement Factor: {db_results['n_plus_one_comparison']['improvement_factor']:.1f}x")
        
        # CPU analysis
        cpu_results = self.results["cpu_intensive"]
        print(f"\n🚀 CPU INTENSIVE ANALYSIS:")
        print(f"  JSON Operations P99: {cpu_results['json_operations']['p99']:.2f} ms")
        print(f"  String Operations P99: {cpu_results['string_operations']['p99']:.2f} ms")
        
        # Performance target evaluation
        print(f"\n🎯 TARGET EVALUATION (P99 < {TARGET_P99_LATENCY} ms):")
        
        issues = []
        if redis_results['get_latency']['p99'] > TARGET_P99_LATENCY:
            issues.append(f"❌ Redis GET P99 ({redis_results['get_latency']['p99']:.2f} ms) exceeds target")
        else:
            print(f"✅ Redis GET P99 ({redis_results['get_latency']['p99']:.2f} ms) meets target")
            
        if db_results['connection_pool']['p99'] > TARGET_P99_LATENCY:
            issues.append(f"❌ DB Connection P99 ({db_results['connection_pool']['p99']:.2f} ms) exceeds target")
        else:
            print(f"✅ DB Connection P99 ({db_results['connection_pool']['p99']:.2f} ms) meets target")
        
        if issues:
            print("\n🚨 PERFORMANCE ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✅ All critical paths meet P99 < 5ms target!")
        
        # Save results to file
        with open("/home/dislove/ACGS-2/performance_hotspot_analysis.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📊 Full results saved to: performance_hotspot_analysis.json")
    
    async def cleanup(self):
        """Clean up connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.db_conn:
            await self.db_conn.close()

async def main():
    analyzer = PerformanceAnalyzer()
    await analyzer.run_full_analysis()

if __name__ == "__main__":
    asyncio.run(main())
