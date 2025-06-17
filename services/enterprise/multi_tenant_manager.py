#!/usr/bin/env python3
"""
ACGS-1 Multi-Tenant Manager
Enterprise-grade multi-tenancy with constitutional governance isolation
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import asyncpg
import redis.asyncio as redis
from fastapi import HTTPException, Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TenantConfig:
    """Tenant configuration with constitutional governance settings"""

    tenant_id: str
    name: str
    constitution_hash: str
    max_users: int
    max_policies: int
    max_governance_actions_per_hour: int
    storage_quota_gb: int
    features: list[str]
    created_at: datetime
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


@dataclass
class TenantMetrics:
    """Tenant usage metrics"""

    tenant_id: str
    active_users: int
    total_policies: int
    governance_actions_last_hour: int
    storage_used_gb: float
    response_time_avg_ms: float
    uptime_percentage: float
    constitutional_compliance_score: float
    last_updated: datetime


class TenantIsolationManager:
    """Manages tenant isolation and resource allocation"""

    def __init__(self, database_url: str, redis_url: str):
        self.database_url = database_url
        self.redis_url = redis_url
        self.tenants: dict[str, TenantConfig] = {}
        self.metrics: dict[str, TenantMetrics] = {}

    async def initialize(self):
        """Initialize tenant manager"""
        self.db_pool = await asyncpg.create_pool(self.database_url)
        self.redis_client = redis.from_url(self.redis_url)
        await self._create_tenant_tables()
        await self._load_tenants()

    async def _create_tenant_tables(self):
        """Create tenant management tables"""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                    tenant_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    constitution_hash VARCHAR(255) NOT NULL,
                    max_users INTEGER DEFAULT 1000,
                    max_policies INTEGER DEFAULT 10000,
                    max_governance_actions_per_hour INTEGER DEFAULT 1000,
                    storage_quota_gb INTEGER DEFAULT 100,
                    features JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT NOW(),
                    status VARCHAR(50) DEFAULT 'active'
                );

                CREATE TABLE IF NOT EXISTS tenant_users (
                    user_id VARCHAR(255),
                    tenant_id VARCHAR(255),
                    role VARCHAR(100),
                    permissions JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY (user_id, tenant_id),
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                );

                CREATE TABLE IF NOT EXISTS tenant_metrics (
                    tenant_id VARCHAR(255),
                    metric_name VARCHAR(100),
                    metric_value FLOAT,
                    recorded_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                );

                CREATE INDEX IF NOT EXISTS idx_tenant_metrics_time
                ON tenant_metrics(tenant_id, recorded_at);
            """
            )

    async def _load_tenants(self):
        """Load existing tenants from database"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tenants WHERE status = 'active'")
            for row in rows:
                tenant = TenantConfig(
                    tenant_id=row["tenant_id"],
                    name=row["name"],
                    constitution_hash=row["constitution_hash"],
                    max_users=row["max_users"],
                    max_policies=row["max_policies"],
                    max_governance_actions_per_hour=row[
                        "max_governance_actions_per_hour"
                    ],
                    storage_quota_gb=row["storage_quota_gb"],
                    features=row["features"],
                    created_at=row["created_at"],
                    status=row["status"],
                )
                self.tenants[tenant.tenant_id] = tenant

        logger.info(f"Loaded {len(self.tenants)} active tenants")

    async def create_tenant(self, tenant_data: dict[str, Any]) -> TenantConfig:
        """Create new tenant with constitutional governance"""
        tenant_id = str(uuid.uuid4())

        # Default constitution hash if not provided
        constitution_hash = tenant_data.get("constitution_hash", "cdd01ef066bc6cf2")

        tenant = TenantConfig(
            tenant_id=tenant_id,
            name=tenant_data["name"],
            constitution_hash=constitution_hash,
            max_users=tenant_data.get("max_users", 1000),
            max_policies=tenant_data.get("max_policies", 10000),
            max_governance_actions_per_hour=tenant_data.get(
                "max_governance_actions_per_hour", 1000
            ),
            storage_quota_gb=tenant_data.get("storage_quota_gb", 100),
            features=tenant_data.get(
                "features", ["basic_governance", "policy_creation"]
            ),
            created_at=datetime.now(),
        )

        # Store in database
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO tenants (
                    tenant_id, name, constitution_hash, max_users, max_policies,
                    max_governance_actions_per_hour, storage_quota_gb, features
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                tenant.tenant_id,
                tenant.name,
                tenant.constitution_hash,
                tenant.max_users,
                tenant.max_policies,
                tenant.max_governance_actions_per_hour,
                tenant.storage_quota_gb,
                json.dumps(tenant.features),
            )

        # Cache tenant
        self.tenants[tenant_id] = tenant
        await self.redis_client.setex(
            f"tenant:{tenant_id}", 3600, json.dumps(tenant.to_dict())
        )

        # Initialize tenant-specific resources
        await self._initialize_tenant_resources(tenant)

        logger.info(f"Created tenant {tenant_id}: {tenant.name}")
        return tenant

    async def _initialize_tenant_resources(self, tenant: TenantConfig):
        """Initialize tenant-specific resources and schemas"""
        async with self.db_pool.acquire() as conn:
            # Create tenant-specific schema
            schema_name = f"tenant_{tenant.tenant_id.replace('-', '_')}"
            await conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')

            # Create tenant-specific tables
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS "{schema_name}".policies (
                    policy_id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content TEXT,
                    status VARCHAR(50) DEFAULT 'draft',
                    constitutional_compliance_score FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS "{schema_name}".governance_actions (
                    action_id VARCHAR(255) PRIMARY KEY,
                    action_type VARCHAR(100) NOT NULL,
                    policy_id VARCHAR(255),
                    user_id VARCHAR(255),
                    constitutional_hash VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """
            )

    async def get_tenant(self, tenant_id: str) -> TenantConfig | None:
        """Get tenant configuration"""
        # Try cache first
        cached = await self.redis_client.get(f"tenant:{tenant_id}")
        if cached:
            data = json.loads(cached)
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            return TenantConfig(**data)

        # Fallback to memory
        return self.tenants.get(tenant_id)

    async def validate_tenant_limits(self, tenant_id: str, action_type: str) -> bool:
        """Validate tenant resource limits"""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return False

        # Check governance actions per hour
        if action_type == "governance_action":
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            actions_count = await self._get_governance_actions_count(
                tenant_id, current_hour
            )
            if actions_count >= tenant.max_governance_actions_per_hour:
                logger.warning(f"Tenant {tenant_id} exceeded governance actions limit")
                return False

        # Check storage quota
        storage_used = await self._get_storage_usage(tenant_id)
        if storage_used >= tenant.storage_quota_gb:
            logger.warning(f"Tenant {tenant_id} exceeded storage quota")
            return False

        return True

    async def _get_governance_actions_count(
        self, tenant_id: str, since: datetime
    ) -> int:
        """Get governance actions count for tenant since timestamp"""
        schema_name = f"tenant_{tenant_id.replace('-', '_')}"
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchval(
                f"""
                SELECT COUNT(*) FROM "{schema_name}".governance_actions
                WHERE created_at >= $1
            """,
                since,
            )
            return result or 0

    async def _get_storage_usage(self, tenant_id: str) -> float:
        """Get storage usage for tenant in GB"""
        schema_name = f"tenant_{tenant_id.replace('-', '_')}"
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT pg_total_relation_size(schemaname||'.'||tablename)::float / (1024*1024*1024)
                FROM pg_tables WHERE schemaname = $1
            """,
                schema_name,
            )
            return result or 0.0

    async def update_tenant_metrics(self, tenant_id: str, metrics: dict[str, float]):
        """Update tenant metrics"""
        async with self.db_pool.acquire() as conn:
            for metric_name, metric_value in metrics.items():
                await conn.execute(
                    """
                    INSERT INTO tenant_metrics (tenant_id, metric_name, metric_value)
                    VALUES ($1, $2, $3)
                """,
                    tenant_id,
                    metric_name,
                    metric_value,
                )

        # Update Redis cache
        await self.redis_client.setex(
            f"tenant_metrics:{tenant_id}", 300, json.dumps(metrics)  # 5 minutes
        )

    async def get_tenant_metrics(self, tenant_id: str) -> dict[str, float] | None:
        """Get current tenant metrics"""
        # Try cache first
        cached = await self.redis_client.get(f"tenant_metrics:{tenant_id}")
        if cached:
            return json.loads(cached)

        # Fallback to database
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT metric_name, metric_value
                FROM tenant_metrics
                WHERE tenant_id = $1
                AND recorded_at > NOW() - INTERVAL '1 hour'
                ORDER BY recorded_at DESC
            """,
                tenant_id,
            )

            metrics = {}
            for row in rows:
                if row["metric_name"] not in metrics:  # Get latest value
                    metrics[row["metric_name"]] = row["metric_value"]

            return metrics

    async def list_tenants(
        self, limit: int = 100, offset: int = 0
    ) -> list[TenantConfig]:
        """List all active tenants"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM tenants
                WHERE status = 'active'
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """,
                limit,
                offset,
            )

            tenants = []
            for row in rows:
                tenant = TenantConfig(
                    tenant_id=row["tenant_id"],
                    name=row["name"],
                    constitution_hash=row["constitution_hash"],
                    max_users=row["max_users"],
                    max_policies=row["max_policies"],
                    max_governance_actions_per_hour=row[
                        "max_governance_actions_per_hour"
                    ],
                    storage_quota_gb=row["storage_quota_gb"],
                    features=row["features"],
                    created_at=row["created_at"],
                    status=row["status"],
                )
                tenants.append(tenant)

            return tenants

    async def update_tenant(
        self, tenant_id: str, update_data: dict[str, Any]
    ) -> TenantConfig | None:
        """Update tenant configuration"""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return None

        # Build update query dynamically
        update_fields = []
        update_values = []
        param_count = 1

        for field, value in update_data.items():
            if field in [
                "name",
                "max_users",
                "max_policies",
                "max_governance_actions_per_hour",
                "storage_quota_gb",
                "features",
                "status",
            ]:
                update_fields.append(f"{field} = ${param_count}")
                if field == "features":
                    update_values.append(json.dumps(value))
                else:
                    update_values.append(value)
                param_count += 1

        if not update_fields:
            return tenant

        update_values.append(tenant_id)  # For WHERE clause

        async with self.db_pool.acquire() as conn:
            await conn.execute(
                f"""
                UPDATE tenants
                SET {', '.join(update_fields)}
                WHERE tenant_id = ${param_count}
            """,
                *update_values,
            )

        # Update cache
        await self.redis_client.delete(f"tenant:{tenant_id}")

        # Return updated tenant
        return await self.get_tenant(tenant_id)

    async def delete_tenant(self, tenant_id: str) -> bool:
        """Soft delete tenant (set status to 'deleted')"""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return False

        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE tenants
                SET status = 'deleted'
                WHERE tenant_id = $1
            """,
                tenant_id,
            )

        # Remove from cache
        await self.redis_client.delete(f"tenant:{tenant_id}")

        logger.info(f"Deleted tenant {tenant_id}")
        return True

    async def get_tenant_metrics(self, tenant_id: str) -> TenantMetrics | None:
        """Get tenant usage metrics"""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return None

        # Get metrics from database
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(DISTINCT policy_id) as total_policies,
                    COALESCE(SUM(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 ELSE 0 END), 0) as governance_actions_last_hour,
                    COALESCE(SUM(storage_used_mb), 0) / 1024.0 as storage_used_gb
                FROM tenant_usage
                WHERE tenant_id = $1
            """,
                tenant_id,
            )

        if not row:
            # Return default metrics if no data
            return TenantMetrics(
                tenant_id=tenant_id,
                active_users=0,
                total_policies=0,
                governance_actions_last_hour=0,
                storage_used_gb=0.0,
                response_time_avg_ms=50.0,
                uptime_percentage=99.9,
                constitutional_compliance_score=100.0,
                last_updated=datetime.now(),
            )

        return TenantMetrics(
            tenant_id=tenant_id,
            active_users=row["active_users"] or 0,
            total_policies=row["total_policies"] or 0,
            governance_actions_last_hour=row["governance_actions_last_hour"] or 0,
            storage_used_gb=float(row["storage_used_gb"] or 0.0),
            response_time_avg_ms=50.0,  # Mock data
            uptime_percentage=99.9,  # Mock data
            constitutional_compliance_score=100.0,  # Mock data
            last_updated=datetime.now(),
        )


class TenantMiddleware:
    """FastAPI middleware for tenant isolation"""

    def __init__(self, tenant_manager: TenantIsolationManager):
        self.tenant_manager = tenant_manager

    async def __call__(self, request: Request, call_next):
        """Process request with tenant context"""
        # Extract tenant ID from header or subdomain
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            # Try to extract from subdomain
            host = request.headers.get("host", "")
            if "." in host:
                subdomain = host.split(".")[0]
                if subdomain != "www":
                    tenant_id = subdomain

        if tenant_id:
            # Validate tenant exists
            tenant = await self.tenant_manager.get_tenant(tenant_id)
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")

            # Add tenant context to request
            request.state.tenant_id = tenant_id
            request.state.tenant = tenant

            # Validate tenant limits for non-GET requests
            if request.method != "GET":
                if not await self.tenant_manager.validate_tenant_limits(
                    tenant_id, "governance_action"
                ):
                    raise HTTPException(
                        status_code=429, detail="Tenant resource limits exceeded"
                    )

        response = await call_next(request)
        return response


# Global tenant manager instance
tenant_manager = TenantIsolationManager(
    database_url=os.getenv(
        "DATABASE_URL", "postgresql://acgs_user:password@localhost:5432/acgs_pgp_db"
    ),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)
