#!/usr/bin/env python3
# Simple Database Performance Test
# Constitutional Hash: cdd01ef066bc6cf2

import subprocess
import time
import json

def run_sql_query(query):
    """Run SQL query using docker exec"""
    cmd = [
        "docker", "exec", "acgs_postgres",
        "psql", "-U", "acgs_user", "-d", "acgs_db",
        "-c", query
    ]
    
    start_time = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.perf_counter()
    
    return (end_time - start_time) * 1000, result.returncode == 0

def test_database_performance():
    """Test database performance"""
    print("🗄️ Testing PostgreSQL database performance...")
    
    # Test simple queries
    simple_query_times = []
    failed_queries = 0
    
    for i in range(100):
        latency, success = run_sql_query("SELECT 1;")
        if success:
            simple_query_times.append(latency)
        else:
            failed_queries += 1
    
    # Test table operations
    print("Creating test data...")
    
    # Create test records
    insert_times = []
    for i in range(50):
        query = f"""
        INSERT INTO agent_confidence_profiles 
        (agent_id, operation_confidence_adjustments, metadata) 
        VALUES ('test_agent_{i}', '{{}}', '{{"test": true}}')
        ON CONFLICT (agent_id) DO UPDATE SET updated_at = NOW();
        """
        latency, success = run_sql_query(query)
        if success:
            insert_times.append(latency)
    
    # Test select operations
    select_times = []
    for i in range(50):
        query = f"SELECT * FROM agent_confidence_profiles WHERE agent_id = 'test_agent_{i}';"
        latency, success = run_sql_query(query)
        if success:
            select_times.append(latency)
    
    # Cleanup
    print("Cleaning up test data...")
    run_sql_query("DELETE FROM agent_confidence_profiles WHERE agent_id LIKE 'test_agent_%';")
    
    # Calculate and print results
    print("\nPostgreSQL Performance Results:")
    print(f"Simple Query Tests: {len(simple_query_times)} successful, {failed_queries} failed")
    
    if simple_query_times:
        print(f"  Average simple query latency: {sum(simple_query_times) / len(simple_query_times):.2f} ms")
        print(f"  P95 simple query latency: {sorted(simple_query_times)[int(0.95 * len(simple_query_times))]:.2f} ms")
        print(f"  P99 simple query latency: {sorted(simple_query_times)[int(0.99 * len(simple_query_times))]:.2f} ms")
    
    if insert_times:
        print(f"  Average INSERT latency: {sum(insert_times) / len(insert_times):.2f} ms")
        print(f"  P95 INSERT latency: {sorted(insert_times)[int(0.95 * len(insert_times))]:.2f} ms")
        print(f"  P99 INSERT latency: {sorted(insert_times)[int(0.99 * len(insert_times))]:.2f} ms")
    
    if select_times:
        print(f"  Average SELECT latency: {sum(select_times) / len(select_times):.2f} ms")
        print(f"  P95 SELECT latency: {sorted(select_times)[int(0.95 * len(select_times))]:.2f} ms")
        print(f"  P99 SELECT latency: {sorted(select_times)[int(0.99 * len(select_times))]:.2f} ms")
    
    # Performance evaluation
    target_p99 = 5.0
    print(f"\n🎯 TARGET EVALUATION (P99 < {target_p99} ms):")
    
    if simple_query_times:
        simple_p99 = sorted(simple_query_times)[int(0.99 * len(simple_query_times))]
        if simple_p99 < target_p99:
            print(f"✅ Simple queries P99 ({simple_p99:.2f} ms) meets target")
        else:
            print(f"❌ Simple queries P99 ({simple_p99:.2f} ms) exceeds target")
    
    if insert_times:
        insert_p99 = sorted(insert_times)[int(0.99 * len(insert_times))]
        if insert_p99 < target_p99:
            print(f"✅ INSERT queries P99 ({insert_p99:.2f} ms) meets target")
        else:
            print(f"❌ INSERT queries P99 ({insert_p99:.2f} ms) exceeds target")
    
    # Save results
    results = {
        "simple_queries": {
            "count": len(simple_query_times),
            "avg_latency": sum(simple_query_times) / len(simple_query_times) if simple_query_times else 0,
            "p95_latency": sorted(simple_query_times)[int(0.95 * len(simple_query_times))] if simple_query_times else 0,
            "p99_latency": sorted(simple_query_times)[int(0.99 * len(simple_query_times))] if simple_query_times else 0
        },
        "insert_queries": {
            "count": len(insert_times),
            "avg_latency": sum(insert_times) / len(insert_times) if insert_times else 0,
            "p95_latency": sorted(insert_times)[int(0.95 * len(insert_times))] if insert_times else 0,
            "p99_latency": sorted(insert_times)[int(0.99 * len(insert_times))] if insert_times else 0
        },
        "select_queries": {
            "count": len(select_times),
            "avg_latency": sum(select_times) / len(select_times) if select_times else 0,
            "p95_latency": sorted(select_times)[int(0.95 * len(select_times))] if select_times else 0,
            "p99_latency": sorted(select_times)[int(0.99 * len(select_times))] if select_times else 0
        }
    }
    
    with open("/home/dislove/ACGS-2/database_performance_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: database_performance_results.json")

if __name__ == "__main__":
    test_database_performance()
