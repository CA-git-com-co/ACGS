#!/usr/bin/env python3
"""
ACGS Database Sharding Manager
Advanced database sharding strategies with constitutional compliance and automatic rebalancing.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

import asyncpg
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ShardingStrategy(Enum):
    """Database sharding strategies."""
    HASH_BASED = "hash_based"
    RANGE_BASED = "range_based"
    DIRECTORY_BASED = "directory_based"
    CONSTITUTIONAL_BASED = "constitutional_based"

class ShardStatus(Enum):
    """Shard status."""
    ACTIVE = "active"
    READONLY = "readonly"
    MIGRATING = "migrating"
    OFFLINE = "offline"

@dataclass
class DatabaseShard:
    """Database shard configuration."""
    shard_id: str
    shard_name: str
    host: str
    port: int
    database: str
    username: str
    password: str
    
    # Shard properties
    status: ShardStatus = ShardStatus.ACTIVE
    weight: float = 1.0
    max_connections: int = 100
    
    # Sharding configuration
    shard_key_start: Optional[str] = None
    shard_key_end: Optional[str] = None
    hash_range_start: Optional[int] = None
    hash_range_end: Optional[int] = None
    
    # Constitutional compliance
    constitutional_compliance_required: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    # Metrics
    connection_count: int = 0
    query_count: int = 0
    data_size_mb: float = 0.0
    last_health_check: Optional[datetime] = None

@dataclass
class ShardingRule:
    """Sharding rule definition."""
    rule_id: str
    table_name: str
    shard_key: str
    strategy: ShardingStrategy
    
    # Rule configuration
    target_shards: List[str] = field(default_factory=list)
    replication_factor: int = 1
    
    # Constitutional compliance
    constitutional_validation_required: bool = False
    constitutional_hash: str = CONSTITUTIONAL_HASH

class DatabaseShardingManager:
    """Advanced database sharding manager for ACGS."""
    
    def __init__(self):
        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()
        
        # Sharding configuration
        self.shards: Dict[str, DatabaseShard] = {}
        self.sharding_rules: Dict[str, ShardingRule] = {}
        self.connection_pools: Dict[str, asyncpg.Pool] = {}
        
        # Routing cache
        self.routing_cache: Dict[str, str] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Migration state
        self.active_migrations: Dict[str, Dict] = {}
        
        # Initialize default sharding configuration
        self.initialize_default_shards()
        self.initialize_sharding_rules()
        
        logger.info("Database Sharding Manager initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for database sharding."""
        self.shard_query_count = Counter(
            'acgs_shard_query_count_total',
            'Total queries per shard',
            ['shard_id', 'query_type'],
            registry=self.registry
        )
        
        self.shard_connection_count = Gauge(
            'acgs_shard_connection_count',
            'Active connections per shard',
            ['shard_id'],
            registry=self.registry
        )
        
        self.shard_data_size = Gauge(
            'acgs_shard_data_size_mb',
            'Data size per shard in MB',
            ['shard_id'],
            registry=self.registry
        )
        
        self.sharding_routing_time = Histogram(
            'acgs_sharding_routing_time_seconds',
            'Time to route queries to shards',
            ['strategy'],
            registry=self.registry
        )
        
        self.constitutional_compliance_sharding = Gauge(
            'acgs_constitutional_compliance_sharding',
            'Constitutional compliance for sharding operations',
            ['shard_id'],
            registry=self.registry
        )

    def initialize_default_shards(self):
        """Initialize default database shards."""
        # Primary shard for critical constitutional data
        primary_shard = DatabaseShard(
            shard_id="shard_primary",
            shard_name="Primary Constitutional Shard",
            host="localhost",
            port=5432,
            database="acgs_primary",
            username="acgs_user",
            password="acgs_password",
            weight=2.0,
            constitutional_compliance_required=True
        )
        self.shards["shard_primary"] = primary_shard
        
        # Secondary shards for general data
        for i in range(1, 4):  # 3 additional shards
            shard = DatabaseShard(
                shard_id=f"shard_{i:02d}",
                shard_name=f"Data Shard {i:02d}",
                host="localhost",
                port=5432 + i,
                database=f"acgs_shard_{i:02d}",
                username="acgs_user",
                password="acgs_password",
                hash_range_start=int((i-1) * (2**32 / 3)),
                hash_range_end=int(i * (2**32 / 3)) - 1,
                constitutional_compliance_required=False
            )
            self.shards[f"shard_{i:02d}"] = shard

    def initialize_sharding_rules(self):
        """Initialize sharding rules for ACGS tables."""
        # Constitutional data - always goes to primary shard
        constitutional_rule = ShardingRule(
            rule_id="constitutional_data",
            table_name="constitutional_policies",
            shard_key="constitutional_hash",
            strategy=ShardingStrategy.CONSTITUTIONAL_BASED,
            target_shards=["shard_primary"],
            constitutional_validation_required=True
        )
        self.sharding_rules["constitutional_data"] = constitutional_rule
        
        # User data - hash-based sharding
        user_rule = ShardingRule(
            rule_id="user_data",
            table_name="users",
            shard_key="user_id",
            strategy=ShardingStrategy.HASH_BASED,
            target_shards=["shard_01", "shard_02", "shard_03"]
        )
        self.sharding_rules["user_data"] = user_rule
        
        # Audit logs - range-based sharding by timestamp
        audit_rule = ShardingRule(
            rule_id="audit_logs",
            table_name="audit_logs",
            shard_key="created_at",
            strategy=ShardingStrategy.RANGE_BASED,
            target_shards=["shard_01", "shard_02", "shard_03"]
        )
        self.sharding_rules["audit_logs"] = audit_rule
        
        # Policy generation data - constitutional-based
        policy_rule = ShardingRule(
            rule_id="policy_generation",
            table_name="policy_generations",
            shard_key="constitutional_hash",
            strategy=ShardingStrategy.CONSTITUTIONAL_BASED,
            target_shards=["shard_primary"],
            constitutional_validation_required=True
        )
        self.sharding_rules["policy_generation"] = policy_rule

    async def start_sharding_manager(self):
        """Start the database sharding manager."""
        logger.info("Starting Database Sharding Manager...")
        
        # Start metrics server
        start_http_server(8108, registry=self.registry)
        logger.info("Sharding manager metrics server started on port 8108")
        
        # Initialize connection pools
        await self.initialize_connection_pools()
        
        # Start monitoring tasks
        asyncio.create_task(self.shard_health_monitoring_loop())
        asyncio.create_task(self.rebalancing_loop())
        asyncio.create_task(self.metrics_collection_loop())
        
        logger.info("Database Sharding Manager started")

    async def initialize_connection_pools(self):
        """Initialize connection pools for all shards."""
        for shard_id, shard in self.shards.items():
            try:
                dsn = f"postgresql://{shard.username}:{shard.password}@{shard.host}:{shard.port}/{shard.database}"
                
                pool = await asyncpg.create_pool(
                    dsn,
                    min_size=5,
                    max_size=shard.max_connections,
                    command_timeout=30
                )
                
                self.connection_pools[shard_id] = pool
                logger.info(f"Initialized connection pool for {shard_id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize connection pool for {shard_id}: {e}")

    async def route_query(self, table_name: str, shard_key_value: Any, query_type: str = "SELECT") -> str:
        """Route query to appropriate shard."""
        start_time = time.time()
        
        try:
            # Find sharding rule for table
            rule = None
            for rule_obj in self.sharding_rules.values():
                if rule_obj.table_name == table_name:
                    rule = rule_obj
                    break
            
            if not rule:
                # Default to primary shard
                shard_id = "shard_primary"
            else:
                shard_id = await self.determine_shard(rule, shard_key_value)
            
            # Record routing time
            self.sharding_routing_time.labels(
                strategy=rule.strategy.value if rule else "default"
            ).observe(time.time() - start_time)
            
            return shard_id
            
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            return "shard_primary"  # Fallback to primary

    async def determine_shard(self, rule: ShardingRule, shard_key_value: Any) -> str:
        """Determine target shard based on sharding rule."""
        try:
            if rule.strategy == ShardingStrategy.CONSTITUTIONAL_BASED:
                return await self.route_constitutional_data(rule, shard_key_value)
            elif rule.strategy == ShardingStrategy.HASH_BASED:
                return await self.route_hash_based(rule, shard_key_value)
            elif rule.strategy == ShardingStrategy.RANGE_BASED:
                return await self.route_range_based(rule, shard_key_value)
            elif rule.strategy == ShardingStrategy.DIRECTORY_BASED:
                return await self.route_directory_based(rule, shard_key_value)
            else:
                return rule.target_shards[0] if rule.target_shards else "shard_primary"
                
        except Exception as e:
            logger.error(f"Error determining shard: {e}")
            return "shard_primary"

    async def route_constitutional_data(self, rule: ShardingRule, shard_key_value: Any) -> str:
        """Route constitutional data to appropriate shard."""
        # Validate constitutional hash
        if rule.constitutional_validation_required:
            if str(shard_key_value) != CONSTITUTIONAL_HASH:
                logger.warning(f"Invalid constitutional hash: {shard_key_value}")
                # Still route to primary but log the violation
        
        # Constitutional data always goes to primary shard
        return "shard_primary"

    async def route_hash_based(self, rule: ShardingRule, shard_key_value: Any) -> str:
        """Route data using hash-based sharding."""
        # Calculate hash
        hash_value = int(hashlib.md5(str(shard_key_value).encode()).hexdigest(), 16)
        hash_32bit = hash_value % (2**32)
        
        # Find shard based on hash range
        for shard_id in rule.target_shards:
            shard = self.shards.get(shard_id)
            if shard and shard.hash_range_start is not None and shard.hash_range_end is not None:
                if shard.hash_range_start <= hash_32bit <= shard.hash_range_end:
                    return shard_id
        
        # Fallback to first target shard
        return rule.target_shards[0] if rule.target_shards else "shard_primary"

    async def route_range_based(self, rule: ShardingRule, shard_key_value: Any) -> str:
        """Route data using range-based sharding."""
        # For timestamp-based sharding (audit logs)
        if isinstance(shard_key_value, datetime):
            # Route based on month
            month = shard_key_value.month
            shard_index = (month - 1) % len(rule.target_shards)
            return rule.target_shards[shard_index]
        
        # For other range-based sharding
        str_value = str(shard_key_value)
        if str_value < "m":  # A-L
            return rule.target_shards[0] if len(rule.target_shards) > 0 else "shard_primary"
        elif str_value < "s":  # M-R
            return rule.target_shards[1] if len(rule.target_shards) > 1 else "shard_primary"
        else:  # S-Z
            return rule.target_shards[2] if len(rule.target_shards) > 2 else "shard_primary"

    async def route_directory_based(self, rule: ShardingRule, shard_key_value: Any) -> str:
        """Route data using directory-based sharding."""
        # Check routing cache first
        cache_key = f"{rule.table_name}:{shard_key_value}"
        
        if cache_key in self.routing_cache:
            return self.routing_cache[cache_key]
        
        # Query directory service (simplified implementation)
        # In practice, this would query a directory service
        shard_id = rule.target_shards[0] if rule.target_shards else "shard_primary"
        
        # Cache the result
        self.routing_cache[cache_key] = shard_id
        
        return shard_id

    async def execute_query(self, query: str, params: tuple = (), table_name: str = "", shard_key_value: Any = None) -> List[Dict]:
        """Execute query on appropriate shard."""
        try:
            # Route to appropriate shard
            shard_id = await self.route_query(table_name, shard_key_value, "SELECT" if query.strip().upper().startswith("SELECT") else "WRITE")
            
            # Get connection pool
            pool = self.connection_pools.get(shard_id)
            if not pool:
                raise RuntimeError(f"No connection pool for shard {shard_id}")
            
            # Execute query
            async with pool.acquire() as connection:
                if query.strip().upper().startswith("SELECT"):
                    result = await connection.fetch(query, *params)
                    self.shard_query_count.labels(shard_id=shard_id, query_type="SELECT").inc()
                    return [dict(row) for row in result]
                else:
                    result = await connection.execute(query, *params)
                    self.shard_query_count.labels(shard_id=shard_id, query_type="WRITE").inc()
                    return [{"affected_rows": result}]
            
        except Exception as e:
            logger.error(f"Error executing query on shard: {e}")
            raise

    async def execute_distributed_query(self, query: str, params: tuple = (), target_shards: List[str] = None) -> Dict[str, List[Dict]]:
        """Execute query across multiple shards."""
        if target_shards is None:
            target_shards = list(self.shards.keys())
        
        results = {}
        
        # Execute query on each target shard
        tasks = []
        for shard_id in target_shards:
            if shard_id in self.connection_pools:
                task = self.execute_query_on_shard(shard_id, query, params)
                tasks.append((shard_id, task))
        
        # Wait for all queries to complete
        for shard_id, task in tasks:
            try:
                result = await task
                results[shard_id] = result
            except Exception as e:
                logger.error(f"Error executing distributed query on {shard_id}: {e}")
                results[shard_id] = []
        
        return results

    async def execute_query_on_shard(self, shard_id: str, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query on specific shard."""
        pool = self.connection_pools.get(shard_id)
        if not pool:
            raise RuntimeError(f"No connection pool for shard {shard_id}")
        
        async with pool.acquire() as connection:
            if query.strip().upper().startswith("SELECT"):
                result = await connection.fetch(query, *params)
                return [dict(row) for row in result]
            else:
                result = await connection.execute(query, *params)
                return [{"affected_rows": result}]

    async def rebalance_shards(self) -> bool:
        """Rebalance data across shards."""
        logger.info("Starting shard rebalancing...")
        
        try:
            # Analyze shard utilization
            shard_stats = await self.collect_shard_statistics()
            
            # Identify imbalanced shards
            imbalanced_shards = self.identify_imbalanced_shards(shard_stats)
            
            if not imbalanced_shards:
                logger.info("No rebalancing needed")
                return True
            
            # Create rebalancing plan
            rebalancing_plan = await self.create_rebalancing_plan(imbalanced_shards, shard_stats)
            
            # Execute rebalancing
            success = await self.execute_rebalancing_plan(rebalancing_plan)
            
            logger.info(f"Shard rebalancing {'completed' if success else 'failed'}")
            return success
            
        except Exception as e:
            logger.error(f"Error during shard rebalancing: {e}")
            return False

    async def collect_shard_statistics(self) -> Dict[str, Dict]:
        """Collect statistics for all shards."""
        stats = {}
        
        for shard_id, shard in self.shards.items():
            try:
                pool = self.connection_pools.get(shard_id)
                if not pool:
                    continue
                
                async with pool.acquire() as connection:
                    # Get database size
                    size_result = await connection.fetchrow(
                        "SELECT pg_database_size(current_database()) as size_bytes"
                    )
                    
                    # Get table counts
                    table_counts = await connection.fetch(
                        "SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del "
                        "FROM pg_stat_user_tables"
                    )
                    
                    stats[shard_id] = {
                        "size_mb": size_result["size_bytes"] / (1024 * 1024),
                        "table_stats": [dict(row) for row in table_counts],
                        "connection_count": len(pool._holders)
                    }
                    
                    # Update metrics
                    self.shard_data_size.labels(shard_id=shard_id).set(stats[shard_id]["size_mb"])
                    self.shard_connection_count.labels(shard_id=shard_id).set(stats[shard_id]["connection_count"])
                    
            except Exception as e:
                logger.error(f"Error collecting stats for {shard_id}: {e}")
                stats[shard_id] = {"size_mb": 0, "table_stats": [], "connection_count": 0}
        
        return stats

    def identify_imbalanced_shards(self, shard_stats: Dict[str, Dict]) -> List[str]:
        """Identify shards that need rebalancing."""
        if len(shard_stats) < 2:
            return []
        
        # Calculate average size
        sizes = [stats["size_mb"] for stats in shard_stats.values()]
        avg_size = sum(sizes) / len(sizes)
        
        # Identify shards significantly above average (>150% of average)
        imbalanced = []
        for shard_id, stats in shard_stats.items():
            if stats["size_mb"] > avg_size * 1.5:
                imbalanced.append(shard_id)
        
        return imbalanced

    async def shard_health_monitoring_loop(self):
        """Monitor shard health continuously."""
        while True:
            try:
                for shard_id, shard in self.shards.items():
                    await self.check_shard_health(shard_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in shard health monitoring: {e}")
                await asyncio.sleep(120)

    async def check_shard_health(self, shard_id: str):
        """Check health of a specific shard."""
        try:
            pool = self.connection_pools.get(shard_id)
            if not pool:
                return
            
            async with pool.acquire() as connection:
                # Simple health check
                await connection.fetchval("SELECT 1")
                
                # Update shard status
                shard = self.shards[shard_id]
                shard.last_health_check = datetime.now(timezone.utc)
                
                if shard.status != ShardStatus.ACTIVE:
                    shard.status = ShardStatus.ACTIVE
                    logger.info(f"Shard {shard_id} is healthy")
                
        except Exception as e:
            logger.error(f"Health check failed for shard {shard_id}: {e}")
            shard = self.shards[shard_id]
            shard.status = ShardStatus.OFFLINE

    def get_sharding_status(self) -> Dict[str, Any]:
        """Get database sharding status."""
        return {
            "total_shards": len(self.shards),
            "active_shards": len([s for s in self.shards.values() if s.status == ShardStatus.ACTIVE]),
            "sharding_rules": len(self.sharding_rules),
            "active_migrations": len(self.active_migrations),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "shards": {
                shard_id: {
                    "status": shard.status.value,
                    "data_size_mb": shard.data_size_mb,
                    "connection_count": shard.connection_count
                }
                for shard_id, shard in self.shards.items()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global database sharding manager instance
sharding_manager = DatabaseShardingManager()

if __name__ == "__main__":
    async def main():
        await sharding_manager.start_sharding_manager()
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down database sharding manager...")
    
    asyncio.run(main())
