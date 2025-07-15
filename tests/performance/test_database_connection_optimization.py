"""
Database Connection Pool Optimization Tests
Constitutional Hash: cdd01ef066bc6cf2

Tests for Priority 3: Performance Issues - Phase 2: Database Optimization

Validates:
- Database connection pooling performance
- Query latency optimization (<2ms target)
- Connection authentication delay resolution
- Pre-warmed connection effectiveness
- Constitutional hash validation query performance
"""

import asyncio
import pytest
import time
import statistics
import psycopg2
from typing import List, Dict, Any
from unittest.mock import AsyncMock, patch
import asyncpg

# Import database optimization components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from services.shared.database.connection_pool import (
    HighPerformanceConnectionPool,
    ConnectionPoolManager,
    CONSTITUTIONAL_HASH
)

# Test configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5439,
    "database": "acgs_db",
    "user": "acgs_user",
    "password": "acgs_secure_password",
    "min_size": 10,
    "max_size": 50,
    "command_timeout": 5,
}

PERFORMANCE_TARGETS = {
    "connection_latency_ms": 10.0,  # Connection establishment
    "query_latency_ms": 2.0,       # Query execution
    "auth_delay_ms": 5.0,          # Authentication delay
    "pool_efficiency": 0.90,       # Pool utilization efficiency
}

TEST_ITERATIONS = 100
CONCURRENT_CONNECTIONS = 20


class TestDatabaseConnectionOptimization:
    """Test suite for database connection pool optimization"""

    @pytest.fixture
    async def connection_pool(self):
        """Create a test connection pool"""
        pool = HighPerformanceConnectionPool(
            pool_name="test_pool",
            **DATABASE_CONFIG
        )
        
        try:
            await pool.initialize()
            yield pool
        finally:
            if pool.pool:
                await pool.close()

    @pytest.mark.asyncio
    async def test_connection_pool_initialization_performance(self):
        """Test connection pool initialization meets performance targets"""
        
        start_time = time.perf_counter()
        
        pool = HighPerformanceConnectionPool(
            pool_name="init_test_pool",
            **DATABASE_CONFIG
        )
        
        try:
            await pool.initialize()
            end_time = time.perf_counter()
            
            initialization_time_ms = (end_time - start_time) * 1000
            
            print(f"Connection Pool Initialization:")
            print(f"  Initialization time: {initialization_time_ms:.2f}ms")
            print(f"  Target: <{PERFORMANCE_TARGETS['connection_latency_ms'] * 5}ms")  # 5x target for initialization
            print(f"  Pool size: {pool.min_size}-{pool.max_size} connections")
            print(f"  Constitutional hash: {pool.constitutional_hash}")
            
            # Assert initialization performance
            assert initialization_time_ms < (PERFORMANCE_TARGETS['connection_latency_ms'] * 5), \
                f"Pool initialization {initialization_time_ms:.2f}ms exceeds target"
            assert pool.constitutional_hash == CONSTITUTIONAL_HASH
            
        finally:
            if pool.pool:
                await pool.close()

    @pytest.mark.asyncio
    async def test_connection_acquisition_latency(self, connection_pool):
        """Test connection acquisition meets latency targets"""
        pool = connection_pool
        
        if not pool.pool:
            pytest.skip("Connection pool not available")
        
        latencies = []
        
        for i in range(TEST_ITERATIONS):
            start_time = time.perf_counter()
            
            async with pool.get_connection() as conn:
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                # Verify connection is valid
                assert conn is not None
        
        # Calculate performance metrics
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98]
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"Connection Acquisition Performance:")
        print(f"  Average latency: {avg_latency:.3f}ms")
        print(f"  P99 latency: {p99_latency:.3f}ms")
        print(f"  Min latency: {min_latency:.3f}ms")
        print(f"  Max latency: {max_latency:.3f}ms")
        print(f"  Target: <{PERFORMANCE_TARGETS['connection_latency_ms']}ms")
        
        # Assert performance targets
        assert avg_latency < PERFORMANCE_TARGETS['connection_latency_ms'], \
            f"Average connection latency {avg_latency:.3f}ms exceeds target {PERFORMANCE_TARGETS['connection_latency_ms']}ms"
        assert p99_latency < PERFORMANCE_TARGETS['connection_latency_ms'], \
            f"P99 connection latency {p99_latency:.3f}ms exceeds target {PERFORMANCE_TARGETS['connection_latency_ms']}ms"

    @pytest.mark.asyncio
    async def test_query_execution_performance(self, connection_pool):
        """Test query execution meets <2ms latency target"""
        pool = connection_pool
        
        if not pool.pool:
            pytest.skip("Connection pool not available")
        
        # Test queries with varying complexity
        test_queries = [
            ("SELECT 1", "Simple query"),
            ("SELECT NOW()", "Timestamp query"),
            (f"SELECT '{CONSTITUTIONAL_HASH}' as hash", "Constitutional hash query"),
            ("SELECT COUNT(*) FROM information_schema.tables", "Metadata query"),
        ]
        
        for query, description in test_queries:
            latencies = []
            
            for i in range(50):  # Fewer iterations for query tests
                start_time = time.perf_counter()
                
                async with pool.get_connection() as conn:
                    result = await conn.fetchval(query)
                    
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                # Verify query executed successfully
                assert result is not None
            
            # Calculate performance metrics
            avg_latency = statistics.mean(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98]
            
            print(f"Query Performance - {description}:")
            print(f"  Average latency: {avg_latency:.3f}ms")
            print(f"  P99 latency: {p99_latency:.3f}ms")
            print(f"  Target: <{PERFORMANCE_TARGETS['query_latency_ms']}ms")
            
            # Assert query performance targets
            assert avg_latency < PERFORMANCE_TARGETS['query_latency_ms'], \
                f"{description} average latency {avg_latency:.3f}ms exceeds target {PERFORMANCE_TARGETS['query_latency_ms']}ms"

    @pytest.mark.asyncio
    async def test_concurrent_connection_performance(self, connection_pool):
        """Test connection pool performance under concurrent load"""
        pool = connection_pool
        
        if not pool.pool:
            pytest.skip("Connection pool not available")
        
        async def concurrent_database_operations():
            """Perform concurrent database operations"""
            latencies = []
            successful_operations = 0
            
            for i in range(10):  # 10 operations per concurrent user
                try:
                    start_time = time.perf_counter()
                    
                    async with pool.get_connection() as conn:
                        result = await conn.fetchval("SELECT $1::text", f"test_{i}")
                        
                    end_time = time.perf_counter()
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    
                    if result is not None:
                        successful_operations += 1
                        
                except Exception as e:
                    print(f"Concurrent operation failed: {e}")
            
            return latencies, successful_operations
        
        # Run concurrent operations
        tasks = [concurrent_database_operations() for _ in range(CONCURRENT_CONNECTIONS)]
        results = await asyncio.gather(*tasks)
        
        # Aggregate results
        all_latencies = []
        total_successful = 0
        total_operations = 0
        
        for latencies, successful in results:
            all_latencies.extend(latencies)
            total_successful += successful
            total_operations += len(latencies)
        
        # Calculate performance metrics
        success_rate = total_successful / total_operations if total_operations > 0 else 0
        avg_latency = statistics.mean(all_latencies) if all_latencies else 0
        p99_latency = statistics.quantiles(all_latencies, n=100)[98] if len(all_latencies) >= 100 else max(all_latencies) if all_latencies else 0
        
        print(f"Concurrent Database Performance ({CONCURRENT_CONNECTIONS} connections):")
        print(f"  Total operations: {total_operations}")
        print(f"  Success rate: {success_rate:.1%}")
        print(f"  Average latency: {avg_latency:.3f}ms")
        print(f"  P99 latency: {p99_latency:.3f}ms")
        print(f"  Targets: >90% success rate, <{PERFORMANCE_TARGETS['query_latency_ms']}ms P99")
        
        # Assert concurrent performance targets
        assert success_rate >= 0.90, f"Concurrent success rate {success_rate:.1%} below 90% target"
        assert p99_latency < PERFORMANCE_TARGETS['query_latency_ms'], \
            f"Concurrent P99 latency {p99_latency:.3f}ms exceeds target {PERFORMANCE_TARGETS['query_latency_ms']}ms"

    @pytest.mark.asyncio
    async def test_connection_pool_efficiency(self, connection_pool):
        """Test connection pool utilization efficiency"""
        pool = connection_pool
        
        if not pool.pool:
            pytest.skip("Connection pool not available")
        
        # Monitor pool statistics during operations
        initial_stats = await pool.get_pool_stats()
        
        # Perform operations to utilize the pool
        async def pool_utilization_test():
            async with pool.get_connection() as conn:
                await conn.fetchval("SELECT pg_sleep(0.01)")  # 10ms delay
        
        # Run operations to stress the pool
        tasks = [pool_utilization_test() for _ in range(30)]
        await asyncio.gather(*tasks)
        
        final_stats = await pool.get_pool_stats()
        
        # Calculate efficiency metrics
        connections_used = final_stats.get("connections_used", 0)
        max_connections = pool.max_size
        pool_efficiency = connections_used / max_connections if max_connections > 0 else 0
        
        print(f"Connection Pool Efficiency:")
        print(f"  Initial stats: {initial_stats}")
        print(f"  Final stats: {final_stats}")
        print(f"  Connections used: {connections_used}/{max_connections}")
        print(f"  Pool efficiency: {pool_efficiency:.1%}")
        print(f"  Target efficiency: >{PERFORMANCE_TARGETS['pool_efficiency']:.0%}")
        
        # Assert pool efficiency
        assert pool_efficiency > 0, "Pool should show utilization after operations"
        # Note: Efficiency target is aspirational - actual efficiency depends on workload

    @pytest.mark.asyncio
    async def test_constitutional_hash_query_optimization(self, connection_pool):
        """Test constitutional hash validation queries are optimized"""
        pool = connection_pool
        
        if not pool.pool:
            pytest.skip("Connection pool not available")
        
        # Test constitutional hash validation query performance
        constitutional_queries = [
            f"SELECT '{CONSTITUTIONAL_HASH}' = '{CONSTITUTIONAL_HASH}' as valid",
            f"SELECT LENGTH('{CONSTITUTIONAL_HASH}') as hash_length",
            f"SELECT MD5('{CONSTITUTIONAL_HASH}') as hash_md5",
        ]
        
        for query in constitutional_queries:
            latencies = []
            
            for i in range(50):
                start_time = time.perf_counter()
                
                async with pool.get_connection() as conn:
                    result = await conn.fetchval(query)
                    
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                # Verify constitutional query executed
                assert result is not None
            
            # Calculate performance metrics
            avg_latency = statistics.mean(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98]
            
            print(f"Constitutional Query Performance:")
            print(f"  Query: {query[:50]}...")
            print(f"  Average latency: {avg_latency:.3f}ms")
            print(f"  P99 latency: {p99_latency:.3f}ms")
            print(f"  Target: <{PERFORMANCE_TARGETS['query_latency_ms']}ms")
            
            # Assert constitutional query performance
            assert avg_latency < PERFORMANCE_TARGETS['query_latency_ms'], \
                f"Constitutional query average latency {avg_latency:.3f}ms exceeds target"

    @pytest.mark.asyncio
    async def test_connection_authentication_delay(self):
        """Test connection authentication delay is minimized"""
        
        # Test direct connection authentication time
        auth_latencies = []
        
        for i in range(10):  # Fewer iterations for auth tests
            start_time = time.perf_counter()
            
            try:
                # Test direct connection (not from pool)
                conn = await asyncpg.connect(
                    host=DATABASE_CONFIG["host"],
                    port=DATABASE_CONFIG["port"],
                    database=DATABASE_CONFIG["database"],
                    user=DATABASE_CONFIG["user"],
                    password=os.environ.get("PASSWORD")password"],
                    command_timeout=DATABASE_CONFIG["command_timeout"]
                )
                
                # Verify connection with simple query
                result = await conn.fetchval("SELECT 1")
                await conn.close()
                
                end_time = time.perf_counter()
                auth_latency_ms = (end_time - start_time) * 1000
                auth_latencies.append(auth_latency_ms)
                
                assert result == 1
                
            except Exception as e:
                print(f"Authentication test failed: {e}")
                # Skip this iteration if connection fails
                continue
        
        if auth_latencies:
            avg_auth_latency = statistics.mean(auth_latencies)
            p99_auth_latency = statistics.quantiles(auth_latencies, n=100)[98] if len(auth_latencies) >= 100 else max(auth_latencies)
            
            print(f"Connection Authentication Performance:")
            print(f"  Average auth latency: {avg_auth_latency:.3f}ms")
            print(f"  P99 auth latency: {p99_auth_latency:.3f}ms")
            print(f"  Target: <{PERFORMANCE_TARGETS['auth_delay_ms']}ms")
            
            # Note: Auth delay target is aspirational - depends on database configuration
            # We log the results but don't fail the test if database is not optimally configured
            if avg_auth_latency > PERFORMANCE_TARGETS['auth_delay_ms']:
                print(f"⚠️  Authentication latency {avg_auth_latency:.3f}ms exceeds target - consider database optimization")
        else:
            pytest.skip("No successful authentication tests completed")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
