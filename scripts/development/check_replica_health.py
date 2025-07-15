#!/usr/bin/env python3
"""
ACGS-1 Read Replica Health Check Script
Monitors health and lag of PostgreSQL read replicas
"""

import asyncio
import json
import time

import asyncpg

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


async def check_replica_health():
    """Check health of all read replicas."""

    replicas = [
        {"name": "primary", "host": "localhost", "port": 5432},
        {"name": "replica1", "host": "localhost", "port": 5433},
        {"name": "replica2", "host": "localhost", "port": 5434},
    ]

    results = []

    for replica in replicas:
        try:
            conn = await asyncpg.connect(
                host=replica["host"],
                port=replica["port"],
                database="acgs_db",
                user="acgs_user",
                password=os.environ.get("PASSWORD"),
                timeout=5,
            )

            # Check basic connectivity
            start_time = time.time()
            result = await conn.fetchval("SELECT 1")
            response_time = time.time() - start_time

            # Check replication lag (for replicas)
            lag_info = None
            if replica["name"] != "primary":
                try:
                    lag_query = """
                    SELECT 
                        CASE 
                            WHEN pg_is_in_recovery() THEN 
                                EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
                            ELSE 0 
                        END as lag_seconds
                    """
                    lag_info = await conn.fetchval(lag_query)
                except:
                    lag_info = None

            await conn.close()

            results.append(
                {
                    "name": replica["name"],
                    "host": replica["host"],
                    "port": replica["port"],
                    "status": "healthy",
                    "response_time": response_time,
                    "lag_seconds": lag_info,
                    "timestamp": time.time(),
                }
            )

        except Exception as e:
            results.append(
                {
                    "name": replica["name"],
                    "host": replica["host"],
                    "port": replica["port"],
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": time.time(),
                }
            )

    return results


async def main():
    """Main health check function."""
    print("🔍 Checking read replica health...")

    results = await check_replica_health()

    print("\n📊 Replica Health Status:")
    print("=" * 50)

    for result in results:
        status_icon = "✅" if result["status"] == "healthy" else "❌"
        print(f"{status_icon} {result['name']:10} ({result['host']}:{result['port']})")

        if result["status"] == "healthy":
            print(f"   Response Time: {result['response_time']:.3f}s")
            if result.get("lag_seconds") is not None:
                print(f"   Replication Lag: {result['lag_seconds']:.2f}s")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        print()

    # Export results to JSON
    with open("logs/replica_health.json", "w") as f:
        json.dump(results, f, indent=2)

    print("📄 Health check results saved to logs/replica_health.json")


if __name__ == "__main__":
    asyncio.run(main())
