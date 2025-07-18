#!/usr/bin/env python3
# Benchmarking Script for Redis Performance
# Constitutional Hash: cdd01ef066bc6cf2

import time
import asyncio
import redis.asyncio as aioredis

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6389,
    "db": 0,
}

async def benchmark_redis_performance():
    redis_client = aioredis.from_url(
        f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}",
        max_connections=50,
        decode_responses=True
    )

    # Measure set/get latency
    set_times = []
    get_times = []

    for i in range(1000):
        key = f"benchmark_key_{i}"
        value = f"benchmark_value_{i}"

        # set operation
        start_time = time.perf_counter()
        await redis_client.set(key, value, ex=600)
        end_time = time.perf_counter()
        set_times.append((end_time - start_time) * 1000)

        # get operation
        start_time = time.perf_counter()
        await redis_client.get(key)
        end_time = time.perf_counter()
        get_times.append((end_time - start_time) * 1000)

    # Cleanup keys
    await redis_client.delete(*(f"benchmark_key_{i}" for i in range(1000)))

    # Calculate and print stats
    print("Redis Benchmark Results:")
    print(f"Average SET latency: {sum(set_times) / len(set_times):.2f} ms")
    print(f"Average GET latency: {sum(get_times) / len(get_times):.2f} ms")
    print(f"P99 SET latency: {sorted(set_times)[int(0.99 * len(set_times))]:.2f} ms")
    print(f"P99 GET latency: {sorted(get_times)[int(0.99 * len(get_times))]:.2f} ms")

asyncio.run(benchmark_redis_performance())
