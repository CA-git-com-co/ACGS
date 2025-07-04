#!/usr/bin/env python3
"""
Cache Monitoring Script for ACGS-1 Advanced Caching
Provides real-time cache performance metrics across all services
"""

import asyncio

import redis

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



async def get_redis_info():
    """Get Redis server information."""
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)

    try:
        info = r.info()
        return {
            "memory_usage": info.get("used_memory_human", "0"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                (
                    info.get("keyspace_hits", 0)
                    / max(
                        info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
                    )
                )
                * 100,
                2,
            ),
        }
    except Exception as e:
        return {"error": str(e)}


async def monitor_cache_performance():
    """Monitor cache performance across all services."""
    services = [
        ("auth_service", 8000),
        ("ac_service", 8001),
        ("integrity_service", 8002),
        ("fv_service", 8003),
        ("gs_service", 8004),
        ("pgc_service", 8005),
        ("ec_service", 8006),
    ]

    print("🔍 ACGS-1 Cache Performance Monitor")
    print("=" * 50)

    redis_info = await get_redis_info()
    print("📊 Redis Server Status:")
    print(f"   Memory Usage: {redis_info.get('memory_usage', 'N/A')}")
    print(f"   Connected Clients: {redis_info.get('connected_clients', 'N/A')}")
    print(f"   Hit Rate: {redis_info.get('hit_rate', 'N/A')}%")
    print()

    for service_name, port in services:
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health") as response:
                    if response.status == 200:
                        print(f"✅ {service_name} (port {port}): Healthy")
                    else:
                        print(f"❌ {service_name} (port {port}): Unhealthy")
        except Exception:
            print(f"❌ {service_name} (port {port}): Not responding")


if __name__ == "__main__":
    asyncio.run(monitor_cache_performance())
