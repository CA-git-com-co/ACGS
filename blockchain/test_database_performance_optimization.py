#!/usr/bin/env python3
"""
Database Performance Optimization Test for ACGS-1
Tests connection pooling, query optimization, indexing, and response times
"""

import asyncio
import asyncpg
import time
import statistics
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration for performance testing."""
    host: str = "localhost"
    port: int = 5432
    database: str = "acgs_db"
    username: str = "acgs_user"
    password: str = "acgs_password"
    min_connections: int = 10
    max_connections: int = 50
    command_timeout: int = 60

@dataclass
class PerformanceMetrics:
    """Performance metrics for database operations."""
    operation: str
    response_times: List[float]
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    errors: List[str]

class DatabasePerformanceOptimizer:
    """Database performance optimization and testing."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_pool = None
        self.metrics = {}
        
    async def initialize(self) -> bool:
        """Initialize database connection pool."""
        try:
            # Create connection pool with optimized settings
            self.connection_pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections,
                command_timeout=self.config.command_timeout,
                # Performance optimizations
                server_settings={
                    'application_name': 'acgs_performance_test',
                    'jit': 'off',  # Disable JIT for consistent performance
                    'shared_preload_libraries': 'pg_stat_statements',
                    'track_activity_query_size': '2048',
                    'log_min_duration_statement': '1000'  # Log slow queries
                }
            )
            
            logger.info("✅ Database connection pool initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            return False
    
    async def test_connection_pooling(self) -> PerformanceMetrics:
        """Test connection pool performance under load."""
        logger.info("🔍 Testing Connection Pool Performance...")
        
        response_times = []
        errors = []
        
        async def test_connection():
            start_time = time.time()
            try:
                async with self.connection_pool.acquire() as conn:
                    # Simple query to test connection
                    result = await conn.fetchval("SELECT 1")
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    return response_time, None
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                return response_time, str(e)
        
        # Test with concurrent connections
        tasks = [test_connection() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                response_times.append(5000)  # Penalty for errors
            else:
                response_time, error = result
                response_times.append(response_time)
                if error:
                    errors.append(error)
        
        return self._calculate_metrics("connection_pooling", response_times, errors)
    
    async def test_query_optimization(self) -> PerformanceMetrics:
        """Test optimized queries performance."""
        logger.info("🔍 Testing Query Optimization...")
        
        response_times = []
        errors = []
        
        # Test queries that should be optimized with indexes
        test_queries = [
            # Constitutional principles query (should use idx_principles_category_priority)
            """
            SELECT id, name, description, priority_weight 
            FROM principles 
            WHERE category = 'constitutional' AND is_active = true 
            ORDER BY priority_weight DESC 
            LIMIT 10
            """,
            
            # Policy status query (should use idx_policies_status_updated)
            """
            SELECT id, title, status, updated_at 
            FROM policies 
            WHERE status IN ('active', 'pending') 
            ORDER BY updated_at DESC 
            LIMIT 20
            """,
            
            # User authentication query (should use idx_users_active_role)
            """
            SELECT id, username, role, is_active 
            FROM users 
            WHERE is_active = true AND role = 'admin'
            LIMIT 5
            """,
            
            # Session validation query (should use idx_sessions_active_user)
            """
            SELECT user_id, expires_at, is_active 
            FROM sessions 
            WHERE is_active = true AND expires_at > NOW() 
            LIMIT 10
            """,
            
            # Governance actions query
            """
            SELECT id, action_type, status, created_at 
            FROM governance_actions 
            WHERE status = 'pending' 
            ORDER BY created_at DESC 
            LIMIT 15
            """
        ]
        
        for query in test_queries:
            for _ in range(10):  # Run each query 10 times
                start_time = time.time()
                try:
                    async with self.connection_pool.acquire() as conn:
                        await conn.fetch(query)
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)
                    errors.append(f"Query error: {str(e)}")
        
        return self._calculate_metrics("query_optimization", response_times, errors)
    
    async def test_concurrent_operations(self) -> PerformanceMetrics:
        """Test database performance under concurrent load."""
        logger.info("🔍 Testing Concurrent Operations...")
        
        response_times = []
        errors = []
        
        async def concurrent_operation(operation_id: int):
            start_time = time.time()
            try:
                async with self.connection_pool.acquire() as conn:
                    # Simulate governance operation
                    async with conn.transaction():
                        # Insert governance action
                        await conn.execute("""
                            INSERT INTO governance_actions (action_type, status, metadata, created_at)
                            VALUES ($1, $2, $3, NOW())
                        """, f"test_action_{operation_id}", "pending", json.dumps({"test": True}))
                        
                        # Query policies
                        await conn.fetch("""
                            SELECT id, title FROM policies 
                            WHERE status = 'active' 
                            LIMIT 5
                        """)
                        
                        # Update action status
                        await conn.execute("""
                            UPDATE governance_actions 
                            SET status = 'completed', updated_at = NOW()
                            WHERE action_type = $1
                        """, f"test_action_{operation_id}")
                
                response_time = (time.time() - start_time) * 1000
                return response_time, None
                
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                return response_time, str(e)
        
        # Run 50 concurrent operations
        tasks = [concurrent_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                response_times.append(5000)  # Penalty for errors
            else:
                response_time, error = result
                response_times.append(response_time)
                if error:
                    errors.append(error)
        
        return self._calculate_metrics("concurrent_operations", response_times, errors)
    
    async def test_index_performance(self) -> PerformanceMetrics:
        """Test index performance and query plan optimization."""
        logger.info("🔍 Testing Index Performance...")
        
        response_times = []
        errors = []
        
        # Test queries that should benefit from indexes
        index_test_queries = [
            # Test constitutional principles index
            ("Constitutional Principles Index", """
                EXPLAIN (ANALYZE, BUFFERS) 
                SELECT * FROM principles 
                WHERE category = 'constitutional' AND is_active = true 
                ORDER BY priority_weight DESC
            """),
            
            # Test policies status index
            ("Policies Status Index", """
                EXPLAIN (ANALYZE, BUFFERS) 
                SELECT * FROM policies 
                WHERE status IN ('active', 'pending') 
                ORDER BY updated_at DESC
            """),
            
            # Test users active role index
            ("Users Active Role Index", """
                EXPLAIN (ANALYZE, BUFFERS) 
                SELECT * FROM users 
                WHERE is_active = true AND role = 'admin'
            """),
        ]
        
        for query_name, query in index_test_queries:
            start_time = time.time()
            try:
                async with self.connection_pool.acquire() as conn:
                    result = await conn.fetch(query)
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)
                    
                    # Check if index is being used
                    query_plan = '\n'.join([row[0] for row in result])
                    if "Index Scan" in query_plan or "Bitmap Index Scan" in query_plan:
                        logger.info(f"✅ {query_name}: Index being used")
                    else:
                        logger.warning(f"⚠️ {query_name}: No index scan detected")
                        
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                errors.append(f"{query_name} error: {str(e)}")
        
        return self._calculate_metrics("index_performance", response_times, errors)
    
    async def test_bulk_operations(self) -> PerformanceMetrics:
        """Test bulk insert/update operations performance."""
        logger.info("🔍 Testing Bulk Operations...")
        
        response_times = []
        errors = []
        
        # Test bulk insert
        start_time = time.time()
        try:
            async with self.connection_pool.acquire() as conn:
                # Prepare bulk data
                bulk_data = [
                    (f"bulk_action_{i}", "pending", json.dumps({"bulk": True, "id": i}))
                    for i in range(100)
                ]
                
                # Bulk insert using copy
                await conn.executemany("""
                    INSERT INTO governance_actions (action_type, status, metadata, created_at)
                    VALUES ($1, $2, $3, NOW())
                """, bulk_data)
                
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
            errors.append(f"Bulk insert error: {str(e)}")
        
        # Test bulk update
        start_time = time.time()
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE governance_actions 
                    SET status = 'completed', updated_at = NOW()
                    WHERE action_type LIKE 'bulk_action_%'
                """)
                
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
            errors.append(f"Bulk update error: {str(e)}")
        
        return self._calculate_metrics("bulk_operations", response_times, errors)
    
    def _calculate_metrics(self, operation: str, response_times: List[float], errors: List[str]) -> PerformanceMetrics:
        """Calculate performance metrics from response times."""
        if not response_times:
            return PerformanceMetrics(
                operation=operation,
                response_times=[],
                avg_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                success_rate=0,
                errors=errors
            )
        
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        success_rate = ((len(response_times) - len(errors)) / len(response_times)) * 100
        
        return PerformanceMetrics(
            operation=operation,
            response_times=response_times,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            success_rate=success_rate,
            errors=errors
        )
    
    async def cleanup(self):
        """Cleanup test data and close connections."""
        try:
            async with self.connection_pool.acquire() as conn:
                # Clean up test data
                await conn.execute("DELETE FROM governance_actions WHERE action_type LIKE 'test_action_%'")
                await conn.execute("DELETE FROM governance_actions WHERE action_type LIKE 'bulk_action_%'")
            
            await self.connection_pool.close()
            logger.info("✅ Database cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

async def test_database_performance_optimization():
    """Main test function for database performance optimization."""
    print("🔍 Testing Database Performance Optimization")
    print("=" * 60)
    
    config = DatabaseConfig()
    optimizer = DatabasePerformanceOptimizer(config)
    
    # Initialize database connection
    if not await optimizer.initialize():
        return {"success": False, "error": "Failed to initialize database"}
    
    try:
        # Run performance tests
        print("⚡ Running Database Performance Tests...")
        
        # Test connection pooling
        pooling_metrics = await optimizer.test_connection_pooling()
        print(f"\n📊 Connection Pooling Results:")
        print(f"   Average Response Time: {pooling_metrics.avg_response_time:.2f}ms")
        print(f"   95th Percentile: {pooling_metrics.p95_response_time:.2f}ms")
        print(f"   Success Rate: {pooling_metrics.success_rate:.1f}%")
        
        # Test query optimization
        query_metrics = await optimizer.test_query_optimization()
        print(f"\n📊 Query Optimization Results:")
        print(f"   Average Response Time: {query_metrics.avg_response_time:.2f}ms")
        print(f"   95th Percentile: {query_metrics.p95_response_time:.2f}ms")
        print(f"   Success Rate: {query_metrics.success_rate:.1f}%")
        
        # Test concurrent operations
        concurrent_metrics = await optimizer.test_concurrent_operations()
        print(f"\n📊 Concurrent Operations Results:")
        print(f"   Average Response Time: {concurrent_metrics.avg_response_time:.2f}ms")
        print(f"   95th Percentile: {concurrent_metrics.p95_response_time:.2f}ms")
        print(f"   Success Rate: {concurrent_metrics.success_rate:.1f}%")
        
        # Test index performance
        index_metrics = await optimizer.test_index_performance()
        print(f"\n📊 Index Performance Results:")
        print(f"   Average Response Time: {index_metrics.avg_response_time:.2f}ms")
        print(f"   95th Percentile: {index_metrics.p95_response_time:.2f}ms")
        print(f"   Success Rate: {index_metrics.success_rate:.1f}%")
        
        # Test bulk operations
        bulk_metrics = await optimizer.test_bulk_operations()
        print(f"\n📊 Bulk Operations Results:")
        print(f"   Average Response Time: {bulk_metrics.avg_response_time:.2f}ms")
        print(f"   95th Percentile: {bulk_metrics.p95_response_time:.2f}ms")
        print(f"   Success Rate: {bulk_metrics.success_rate:.1f}%")
        
        # Calculate overall performance
        all_metrics = [pooling_metrics, query_metrics, concurrent_metrics, index_metrics, bulk_metrics]
        overall_avg = statistics.mean([m.avg_response_time for m in all_metrics])
        overall_p95 = statistics.mean([m.p95_response_time for m in all_metrics])
        overall_success = statistics.mean([m.success_rate for m in all_metrics])
        
        print(f"\n📈 Overall Performance Summary:")
        print(f"   Overall Average Response Time: {overall_avg:.2f}ms")
        print(f"   Overall 95th Percentile: {overall_p95:.2f}ms")
        print(f"   Overall Success Rate: {overall_success:.1f}%")
        
        # Target validation
        target_response_time = 50.0  # ms
        target_success_rate = 95.0   # %
        
        meets_response_target = overall_p95 <= target_response_time
        meets_success_target = overall_success >= target_success_rate
        
        print(f"\n🎯 Target Validation:")
        print(f"   Target Response Time (95th percentile): ≤{target_response_time}ms")
        print(f"   Achieved Response Time: {overall_p95:.2f}ms")
        print(f"   Response Time Target: {'✅ MET' if meets_response_target else '❌ NOT MET'}")
        print(f"   Target Success Rate: ≥{target_success_rate}%")
        print(f"   Achieved Success Rate: {overall_success:.1f}%")
        print(f"   Success Rate Target: {'✅ MET' if meets_success_target else '❌ NOT MET'}")
        
        return {
            "success": True,
            "overall_avg_response_time": overall_avg,
            "overall_p95_response_time": overall_p95,
            "overall_success_rate": overall_success,
            "meets_response_target": meets_response_target,
            "meets_success_target": meets_success_target,
            "metrics": {
                "connection_pooling": pooling_metrics,
                "query_optimization": query_metrics,
                "concurrent_operations": concurrent_metrics,
                "index_performance": index_metrics,
                "bulk_operations": bulk_metrics
            }
        }
        
    finally:
        await optimizer.cleanup()

async def main():
    """Main function."""
    print("🚀 Starting Database Performance Optimization Test")
    print("=" * 70)
    
    result = await test_database_performance_optimization()
    
    if result["success"]:
        print("\n🎯 Database Performance Summary")
        print("=" * 50)
        print(f"⚡ Average Response Time: {result['overall_avg_response_time']:.2f}ms")
        print(f"📊 95th Percentile Response Time: {result['overall_p95_response_time']:.2f}ms")
        print(f"✅ Success Rate: {result['overall_success_rate']:.1f}%")
        print(f"🎯 Response Time Target: {'MET' if result['meets_response_target'] else 'NOT MET'}")
        print(f"🎯 Success Rate Target: {'MET' if result['meets_success_target'] else 'NOT MET'}")
        
        if result["meets_response_target"] and result["meets_success_target"]:
            print("\n🎉 Database performance optimization successful!")
            exit(0)
        else:
            print("\n⚠️ Database performance targets not fully met.")
            exit(1)
    else:
        print("\n❌ Database performance optimization test failed.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
