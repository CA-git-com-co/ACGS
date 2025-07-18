#!/usr/bin/env python3
# Benchmarking Script for PostgreSQL Performance
# Constitutional Hash: cdd01ef066bc6cf2

import time
import asyncio
import asyncpg
import os

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5439,
    "user": "acgs_user",
    "password": os.environ.get("POSTGRES_PASSWORD", "acgs_password"),
    "database": "acgs_db",
}

async def benchmark_postgresql_performance():
    # Connect to database
    conn = await asyncpg.connect(
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"],
        database=DATABASE_CONFIG["database"],
    )

    # Test simple query performance
    simple_query_times = []
    for i in range(1000):
        start_time = time.perf_counter()
        await conn.fetchval("SELECT 1")
        end_time = time.perf_counter()
        simple_query_times.append((end_time - start_time) * 1000)

    # Test insert performance
    insert_times = []
    for i in range(100):
        start_time = time.perf_counter()
        await conn.execute(
            """
            INSERT INTO agent_confidence_profiles 
            (agent_id, operation_confidence_adjustments, metadata) 
            VALUES ($1, $2, $3)
            ON CONFLICT (agent_id) DO UPDATE SET 
            updated_at = NOW()
            """,
            f"benchmark_agent_{i}",
            "{}",
            '{"test": true}',
        )
        end_time = time.perf_counter()
        insert_times.append((end_time - start_time) * 1000)

    # Test select performance
    select_times = []
    for i in range(100):
        start_time = time.perf_counter()
        await conn.fetch(
            "SELECT * FROM agent_confidence_profiles WHERE agent_id = $1",
            f"benchmark_agent_{i}"
        )
        end_time = time.perf_counter()
        select_times.append((end_time - start_time) * 1000)

    # Cleanup
    await conn.execute("DELETE FROM agent_confidence_profiles WHERE agent_id LIKE 'benchmark_agent_%'")
    await conn.close()

    # Calculate and print stats
    print("PostgreSQL Benchmark Results:")
    print(f"Average simple query latency: {sum(simple_query_times) / len(simple_query_times):.2f} ms")
    print(f"P99 simple query latency: {sorted(simple_query_times)[int(0.99 * len(simple_query_times))]:.2f} ms")
    print(f"Average INSERT latency: {sum(insert_times) / len(insert_times):.2f} ms")
    print(f"P99 INSERT latency: {sorted(insert_times)[int(0.99 * len(insert_times))]:.2f} ms")
    print(f"Average SELECT latency: {sum(select_times) / len(select_times):.2f} ms")
    print(f"P99 SELECT latency: {sorted(select_times)[int(0.99 * len(select_times))]:.2f} ms")

asyncio.run(benchmark_postgresql_performance())
