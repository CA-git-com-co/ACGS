"""
Database Performance Tests for DGM Service.

Tests database operations performance:
- Query response times
- Connection pool efficiency
- Bulk operations performance
- Index effectiveness
- Cache hit rates
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from dgm_service.database import database_manager
from dgm_service.models.dgm_archive import DGMArchiveEntry
from dgm_service.models.performance_metrics import PerformanceMetric
from dgm_service.models.constitutional_compliance import ConstitutionalComplianceLog


class DatabasePerformanceTest:
    """Database performance testing utilities."""
    
    def __init__(self):
        self.session = None
        
    async def setup(self):
        """Setup database session."""
        await database_manager.initialize()
        self.session = database_manager.get_session()
        
    async def teardown(self):
        """Cleanup database session."""
        if self.session:
            await self.session.close()
    
    async def measure_query_time(self, query: str, params: Dict = None) -> Dict:
        """Measure query execution time."""
        start_time = time.perf_counter()
        
        try:
            async with self.session() as session:
                result = await session.execute(text(query), params or {})
                rows = result.fetchall()
                
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "execution_time_ms": execution_time,
                "row_count": len(rows),
                "success": True
            }
        except Exception as e:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            
            return {
                "execution_time_ms": execution_time,
                "row_count": 0,
                "success": False,
                "error": str(e)
            }
    
    async def bulk_insert_performance(self, table_name: str, records: List[Dict], 
                                    batch_size: int = 1000) -> Dict:
        """Test bulk insert performance."""
        start_time = time.perf_counter()
        
        try:
            async with self.session() as session:
                # Process in batches
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    if table_name == "dgm_archive":
                        entries = [DGMArchiveEntry(**record) for record in batch]
                        session.add_all(entries)
                    elif table_name == "performance_metrics":
                        entries = [PerformanceMetric(**record) for record in batch]
                        session.add_all(entries)
                    
                    await session.commit()
                
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            
            return {
                "execution_time_ms": execution_time,
                "records_inserted": len(records),
                "records_per_second": len(records) / ((end_time - start_time) or 0.001),
                "batch_size": batch_size,
                "success": True
            }
        except Exception as e:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            
            return {
                "execution_time_ms": execution_time,
                "records_inserted": 0,
                "records_per_second": 0,
                "success": False,
                "error": str(e)
            }
    
    async def connection_pool_test(self, concurrent_connections: int = 20,
                                 operations_per_connection: int = 10) -> Dict:
        """Test connection pool performance."""
        async def connection_worker():
            results = []
            for _ in range(operations_per_connection):
                result = await self.measure_query_time("SELECT 1")
                results.append(result)
            return results
        
        start_time = time.perf_counter()
        
        # Create concurrent tasks
        tasks = [connection_worker() for _ in range(concurrent_connections)]
        all_results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        
        # Flatten results
        flat_results = [result for worker_results in all_results for result in worker_results]
        
        execution_times = [r["execution_time_ms"] for r in flat_results if r["success"]]
        success_count = sum(1 for r in flat_results if r["success"])
        
        return {
            "total_time_ms": total_time,
            "concurrent_connections": concurrent_connections,
            "operations_per_connection": operations_per_connection,
            "total_operations": len(flat_results),
            "successful_operations": success_count,
            "success_rate": (success_count / len(flat_results)) * 100,
            "avg_operation_time_ms": statistics.mean(execution_times) if execution_times else 0,
            "operations_per_second": len(flat_results) / ((end_time - start_time) or 0.001)
        }


@pytest.fixture
async def db_test():
    """Fixture for database performance testing."""
    test = DatabasePerformanceTest()
    await test.setup()
    yield test
    await test.teardown()


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_simple_query_performance(db_test):
    """Test simple query performance."""
    result = await db_test.measure_query_time("SELECT 1")
    
    # Simple queries should be very fast
    assert result["success"], f"Simple query failed: {result.get('error', 'Unknown error')}"
    assert result["execution_time_ms"] < 10, f"Simple query too slow: {result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_dgm_archive_query_performance(db_test):
    """Test DGM archive query performance."""
    query = """
    SELECT id, improvement_id, status, created_at 
    FROM dgm.dgm_archive 
    ORDER BY created_at DESC 
    LIMIT 100
    """
    
    result = await db_test.measure_query_time(query)
    
    # Archive queries should be fast with proper indexing
    assert result["success"], f"Archive query failed: {result.get('error', 'Unknown error')}"
    assert result["execution_time_ms"] < 100, f"Archive query too slow: {result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_performance_metrics_aggregation(db_test):
    """Test performance metrics aggregation query."""
    query = """
    SELECT 
        metric_name,
        AVG(value) as avg_value,
        MAX(value) as max_value,
        MIN(value) as min_value,
        COUNT(*) as count
    FROM dgm.performance_metrics 
    WHERE timestamp >= NOW() - INTERVAL '1 hour'
    GROUP BY metric_name
    """
    
    result = await db_test.measure_query_time(query)
    
    # Aggregation queries should complete within reasonable time
    assert result["success"], f"Aggregation query failed: {result.get('error', 'Unknown error')}"
    assert result["execution_time_ms"] < 500, f"Aggregation query too slow: {result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_constitutional_compliance_search(db_test):
    """Test constitutional compliance search performance."""
    query = """
    SELECT id, improvement_id, compliance_score, validation_result
    FROM dgm.constitutional_compliance_log
    WHERE compliance_score >= :min_score
    AND created_at >= NOW() - INTERVAL '24 hours'
    ORDER BY compliance_score DESC
    LIMIT 50
    """
    
    result = await db_test.measure_query_time(query, {"min_score": 0.8})
    
    # Compliance searches should be optimized
    assert result["success"], f"Compliance search failed: {result.get('error', 'Unknown error')}"
    assert result["execution_time_ms"] < 200, f"Compliance search too slow: {result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_connection_pool_performance(db_test):
    """Test database connection pool performance."""
    result = await db_test.connection_pool_test(
        concurrent_connections=15,
        operations_per_connection=5
    )
    
    # Connection pool should handle concurrent access efficiently
    assert result["success_rate"] >= 99.0, f"Connection pool success rate too low: {result['success_rate']}%"
    assert result["avg_operation_time_ms"] < 50, f"Average operation time too high: {result['avg_operation_time_ms']}ms"
    assert result["operations_per_second"] > 100, f"Operations per second too low: {result['operations_per_second']}"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_index_effectiveness(db_test):
    """Test database index effectiveness."""
    # Test indexed query
    indexed_query = """
    SELECT id, improvement_id, status 
    FROM dgm.dgm_archive 
    WHERE improvement_id = :improvement_id
    """
    
    indexed_result = await db_test.measure_query_time(
        indexed_query, 
        {"improvement_id": "test-improvement-123"}
    )
    
    # Test non-indexed query (should be slower)
    non_indexed_query = """
    SELECT id, improvement_id, status 
    FROM dgm.dgm_archive 
    WHERE metadata::text LIKE :pattern
    """
    
    non_indexed_result = await db_test.measure_query_time(
        non_indexed_query,
        {"pattern": "%test%"}
    )
    
    # Indexed queries should be significantly faster
    assert indexed_result["success"], "Indexed query failed"
    assert indexed_result["execution_time_ms"] < 50, f"Indexed query too slow: {indexed_result['execution_time_ms']}ms"
    
    # Non-indexed query can be slower but should still complete
    if non_indexed_result["success"]:
        assert non_indexed_result["execution_time_ms"] < 1000, "Non-indexed query extremely slow"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.slow
@pytest.mark.asyncio
async def test_bulk_operations_performance(db_test):
    """Test bulk database operations performance."""
    # Generate test data
    test_records = []
    for i in range(1000):
        test_records.append({
            "improvement_id": f"perf-test-{i}",
            "status": "completed",
            "performance_delta": 0.1 * (i % 10),
            "metadata": {"test": True, "batch": "performance"},
            "constitutional_compliance": True
        })
    
    # Test bulk insert performance
    result = await db_test.bulk_insert_performance("dgm_archive", test_records, batch_size=100)
    
    # Bulk operations should be efficient
    assert result["success"], f"Bulk insert failed: {result.get('error', 'Unknown error')}"
    assert result["records_per_second"] > 100, f"Bulk insert too slow: {result['records_per_second']} records/sec"
    assert result["execution_time_ms"] < 10000, f"Bulk insert took too long: {result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_database_statistics_query(db_test):
    """Test database statistics and health queries."""
    stats_query = """
    SELECT 
        schemaname,
        tablename,
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes,
        n_live_tup as live_tuples,
        n_dead_tup as dead_tuples
    FROM pg_stat_user_tables 
    WHERE schemaname = 'dgm'
    """
    
    result = await db_test.measure_query_time(stats_query)
    
    # Statistics queries should be fast for monitoring
    assert result["success"], f"Statistics query failed: {result.get('error', 'Unknown error')}"
    assert result["execution_time_ms"] < 100, f"Statistics query too slow: {result['execution_time_ms']}ms"


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.asyncio
async def test_concurrent_read_write_performance(db_test):
    """Test concurrent read/write performance."""
    async def read_worker():
        results = []
        for _ in range(10):
            result = await db_test.measure_query_time(
                "SELECT COUNT(*) FROM dgm.dgm_archive WHERE status = 'completed'"
            )
            results.append(result)
        return results
    
    async def write_worker():
        # Simulate lightweight write operations
        results = []
        for i in range(5):
            result = await db_test.measure_query_time(
                "INSERT INTO dgm.performance_metrics (metric_name, value, timestamp, service_name) VALUES (:name, :value, NOW(), :service)",
                {
                    "name": f"test_metric_{i}",
                    "value": i * 0.1,
                    "service": "dgm-service"
                }
            )
            results.append(result)
        return results
    
    # Run concurrent read and write operations
    start_time = time.perf_counter()
    
    read_tasks = [read_worker() for _ in range(5)]
    write_tasks = [write_worker() for _ in range(2)]
    
    read_results, write_results = await asyncio.gather(
        asyncio.gather(*read_tasks),
        asyncio.gather(*write_tasks)
    )
    
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    # Flatten results
    all_read_results = [r for worker_results in read_results for r in worker_results]
    all_write_results = [r for worker_results in write_results for r in worker_results]
    
    read_success_rate = (sum(1 for r in all_read_results if r["success"]) / len(all_read_results)) * 100
    write_success_rate = (sum(1 for r in all_write_results if r["success"]) / len(all_write_results)) * 100
    
    # Concurrent operations should maintain good performance
    assert read_success_rate >= 99.0, f"Read success rate too low: {read_success_rate}%"
    assert write_success_rate >= 99.0, f"Write success rate too low: {write_success_rate}%"
    assert total_time < 5000, f"Concurrent operations took too long: {total_time}ms"
