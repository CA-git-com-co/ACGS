#!/usr/bin/env python3
"""
ACGS-1 Enterprise API Gateway
Advanced resource management and scaling for >10,000 concurrent users
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime

import asyncpg
import httpx
import redis.asyncio as redis
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter(
    "acgs_enterprise_requests_total",
    "Total enterprise API requests",
    ["tenant_id", "endpoint", "method", "status"],
)

request_duration = Histogram(
    "acgs_enterprise_request_duration_seconds",
    "Enterprise API request duration",
    ["tenant_id", "endpoint", "method"],
)

active_connections = Gauge(
    "acgs_enterprise_active_connections", "Active enterprise connections", ["tenant_id"]
)

resource_usage = Gauge(
    "acgs_enterprise_resource_usage",
    "Enterprise resource usage",
    ["tenant_id", "resource_type"],
)


@dataclass
class ResourceQuota:
    """Resource quota configuration for enterprise tenants"""

    tenant_id: str
    max_requests_per_minute: int
    max_concurrent_connections: int
    max_storage_gb: int
    max_governance_actions_per_hour: int
    max_policy_synthesis_requests_per_hour: int
    priority_level: int  # 1-10, higher = more priority


class EnterpriseResourceManager:
    """Manages enterprise resource allocation and scaling"""

    def __init__(self, redis_url: str, database_url: str):
        self.redis_url = redis_url
        self.database_url = database_url
        self.quotas: dict[str, ResourceQuota] = {}
        self.connection_pools: dict[str, int] = {}

    async def initialize(self):
        """Initialize resource manager"""
        self.redis_client = redis.from_url(self.redis_url)
        self.db_pool = await asyncpg.create_pool(self.database_url)
        await self._load_resource_quotas()

    async def _load_resource_quotas(self):
        """Load resource quotas from configuration"""
        # Default enterprise quotas
        {
            "enterprise_premium": ResourceQuota(
                tenant_id="default",
                max_requests_per_minute=10000,
                max_concurrent_connections=1000,
                max_storage_gb=1000,
                max_governance_actions_per_hour=5000,
                max_policy_synthesis_requests_per_hour=1000,
                priority_level=9,
            ),
            "enterprise_standard": ResourceQuota(
                tenant_id="default",
                max_requests_per_minute=5000,
                max_concurrent_connections=500,
                max_storage_gb=500,
                max_governance_actions_per_hour=2000,
                max_policy_synthesis_requests_per_hour=500,
                priority_level=7,
            ),
            "enterprise_basic": ResourceQuota(
                tenant_id="default",
                max_requests_per_minute=1000,
                max_concurrent_connections=100,
                max_storage_gb=100,
                max_governance_actions_per_hour=500,
                max_policy_synthesis_requests_per_hour=100,
                priority_level=5,
            ),
        }

        # Load tenant-specific quotas from database
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT tenant_id, quota_config
                FROM tenant_quotas
                WHERE active = true
            """
            )

            for row in rows:
                config = row["quota_config"]
                quota = ResourceQuota(
                    tenant_id=row["tenant_id"],
                    max_requests_per_minute=config.get("max_requests_per_minute", 1000),
                    max_concurrent_connections=config.get("max_concurrent_connections", 100),
                    max_storage_gb=config.get("max_storage_gb", 100),
                    max_governance_actions_per_hour=config.get(
                        "max_governance_actions_per_hour", 500
                    ),
                    max_policy_synthesis_requests_per_hour=config.get(
                        "max_policy_synthesis_requests_per_hour", 100
                    ),
                    priority_level=config.get("priority_level", 5),
                )
                self.quotas[row["tenant_id"]] = quota

        logger.info(f"Loaded resource quotas for {len(self.quotas)} tenants")

    async def check_rate_limit(self, tenant_id: str, endpoint: str) -> bool:
        """Check if request is within rate limits"""
        quota = self.quotas.get(tenant_id)
        if not quota:
            return False

        # Check requests per minute
        current_minute = int(time.time() / 60)
        key = f"rate_limit:{tenant_id}:{current_minute}"

        current_count = await self.redis_client.get(key)
        current_count = int(current_count) if current_count else 0

        if current_count >= quota.max_requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for tenant {tenant_id}: {current_count}/{quota.max_requests_per_minute}"
            )
            return False

        # Increment counter
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, 60)

        return True

    async def check_connection_limit(self, tenant_id: str) -> bool:
        """Check if tenant is within connection limits"""
        quota = self.quotas.get(tenant_id)
        if not quota:
            return False

        current_connections = self.connection_pools.get(tenant_id, 0)
        return current_connections < quota.max_concurrent_connections

    async def acquire_connection(self, tenant_id: str):
        """Acquire connection for tenant"""
        self.connection_pools[tenant_id] = self.connection_pools.get(tenant_id, 0) + 1
        active_connections.labels(tenant_id=tenant_id).set(self.connection_pools[tenant_id])

    async def release_connection(self, tenant_id: str):
        """Release connection for tenant"""
        if tenant_id in self.connection_pools:
            self.connection_pools[tenant_id] = max(0, self.connection_pools[tenant_id] - 1)
            active_connections.labels(tenant_id=tenant_id).set(self.connection_pools[tenant_id])

    async def get_resource_usage(self, tenant_id: str) -> dict[str, float]:
        """Get current resource usage for tenant"""
        usage = {}

        # Get from Redis cache
        cached_usage = await self.redis_client.get(f"resource_usage:{tenant_id}")
        if cached_usage:
            usage = json.loads(cached_usage)
        else:
            # Calculate from database
            async with self.db_pool.acquire() as conn:
                # Storage usage
                storage_result = await conn.fetchval(
                    """
                    SELECT COALESCE(SUM(size_bytes), 0) / (1024*1024*1024.0) as storage_gb
                    FROM tenant_storage_usage
                    WHERE tenant_id = $1
                """,
                    tenant_id,
                )
                usage["storage_gb"] = float(storage_result or 0)

                # Governance actions in last hour
                governance_result = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM governance_actions
                    WHERE tenant_id = $1
                    AND created_at > NOW() - INTERVAL '1 hour'
                """,
                    tenant_id,
                )
                usage["governance_actions_last_hour"] = int(governance_result or 0)

            # Cache for 5 minutes
            await self.redis_client.setex(f"resource_usage:{tenant_id}", 300, json.dumps(usage))

        return usage


class EnterpriseLoadBalancer:
    """Intelligent load balancer for enterprise workloads"""

    def __init__(self, service_endpoints: dict[str, list[str]]):
        self.service_endpoints = service_endpoints
        self.service_health: dict[str, dict[str, bool]] = {}
        self.service_load: dict[str, dict[str, float]] = {}

    async def initialize(self):
        """Initialize load balancer"""
        await self._initialize_health_checks()

    async def _initialize_health_checks(self):
        """Initialize health checking for all services"""
        for service_name, endpoints in self.service_endpoints.items():
            self.service_health[service_name] = {}
            self.service_load[service_name] = {}

            for endpoint in endpoints:
                self.service_health[service_name][endpoint] = True
                self.service_load[service_name][endpoint] = 0.0

    async def get_best_endpoint(self, service_name: str, tenant_priority: int = 5) -> str | None:
        """Get best endpoint for service based on health and load"""
        if service_name not in self.service_endpoints:
            return None

        healthy_endpoints = []
        for endpoint in self.service_endpoints[service_name]:
            if self.service_health[service_name].get(endpoint, False):
                load = self.service_load[service_name].get(endpoint, 0.0)
                healthy_endpoints.append((endpoint, load))

        if not healthy_endpoints:
            return None

        # Sort by load (ascending) and return least loaded
        healthy_endpoints.sort(key=lambda x: x[1])
        return healthy_endpoints[0][0]

    async def update_service_load(self, service_name: str, endpoint: str, load: float):
        """Update service load metrics"""
        if service_name in self.service_load and endpoint in self.service_load[service_name]:
            self.service_load[service_name][endpoint] = load

    async def health_check_service(self, service_name: str, endpoint: str) -> bool:
        """Perform health check on service endpoint"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{endpoint}/health")
                healthy = response.status_code == 200
                self.service_health[service_name][endpoint] = healthy
                return healthy
        except Exception as e:
            logger.warning(f"Health check failed for {service_name} at {endpoint}: {e}")
            self.service_health[service_name][endpoint] = False
            return False


class EnterpriseAPIGateway:
    """Enterprise API Gateway with advanced features"""

    def __init__(self):
        self.app = FastAPI(
            title="ACGS-1 Enterprise API Gateway",
            version="3.0.0",
            description="Enterprise-grade API gateway for constitutional governance",
        )
        self.resource_manager = EnterpriseResourceManager(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql://acgs_user:password@localhost:5432/acgs_pgp_db",
            ),
        )
        self.load_balancer = EnterpriseLoadBalancer(
            {
                "auth": ["http://localhost:8000"],
                "ac": ["http://localhost:8001"],
                "integrity": ["http://localhost:8002"],
                "fv": ["http://localhost:8003"],
                "gs": ["http://localhost:8004"],
                "pgc": ["http://localhost:8005"],
                "ec": ["http://localhost:8006"],
            }
        )

        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Setup middleware for enterprise features"""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Custom enterprise middleware
        @self.app.middleware("http")
        async def enterprise_middleware(request: Request, call_next):
            start_time = time.time()

            # Extract tenant ID
            tenant_id = request.headers.get("X-Tenant-ID", "default")

            # Check rate limits
            if not await self.resource_manager.check_rate_limit(tenant_id, request.url.path):
                return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})

            # Check connection limits
            if not await self.resource_manager.check_connection_limit(tenant_id):
                return JSONResponse(status_code=503, content={"error": "Connection limit exceeded"})

            # Acquire connection
            await self.resource_manager.acquire_connection(tenant_id)

            try:
                response = await call_next(request)

                # Record metrics
                duration = time.time() - start_time
                request_duration.labels(
                    tenant_id=tenant_id,
                    endpoint=request.url.path,
                    method=request.method,
                ).observe(duration)

                request_count.labels(
                    tenant_id=tenant_id,
                    endpoint=request.url.path,
                    method=request.method,
                    status=response.status_code,
                ).inc()

                return response

            finally:
                # Release connection
                await self.resource_manager.release_connection(tenant_id)

    def _setup_routes(self):
        """Setup API gateway routes"""

        @self.app.get("/health")
        async def health_check():
            """Gateway health check"""
            return {
                "status": "healthy",
                "service": "enterprise_gateway",
                "version": "3.0.0",
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.get("/metrics")
        async def get_metrics():
            """Prometheus metrics endpoint"""
            return Response(content=generate_latest(), media_type="text/plain")

        @self.app.get("/enterprise/resource-usage/{tenant_id}")
        async def get_resource_usage(tenant_id: str):
            """Get resource usage for tenant"""
            usage = await self.resource_manager.get_resource_usage(tenant_id)
            return {"tenant_id": tenant_id, "usage": usage}

        @self.app.post("/enterprise/proxy/{service_name}")
        async def proxy_request(
            service_name: str, request: Request, background_tasks: BackgroundTasks
        ):
            """Proxy request to backend service with load balancing"""
            tenant_id = request.headers.get("X-Tenant-ID", "default")

            # Get best endpoint
            endpoint = await self.load_balancer.get_best_endpoint(service_name)
            if not endpoint:
                raise HTTPException(status_code=503, detail="Service unavailable")

            # Proxy request
            async with httpx.AsyncClient() as client:
                # Forward headers
                headers = dict(request.headers)
                headers["X-Forwarded-For"] = request.client.host
                headers["X-Tenant-ID"] = tenant_id

                # Get request body
                body = await request.body()

                # Make request
                response = await client.request(
                    method=request.method,
                    url=f"{endpoint}{request.url.path}",
                    headers=headers,
                    content=body,
                    params=request.query_params,
                )

                # Update load metrics in background
                background_tasks.add_task(
                    self.load_balancer.update_service_load,
                    service_name,
                    endpoint,
                    response.elapsed.total_seconds(),
                )

                return JSONResponse(
                    content=(
                        response.json()
                        if response.headers.get("content-type", "").startswith("application/json")
                        else response.text
                    ),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

    async def startup(self):
        """Startup tasks"""
        await self.resource_manager.initialize()
        await self.load_balancer.initialize()
        logger.info("Enterprise API Gateway started")

    async def shutdown(self):
        """Shutdown tasks"""
        logger.info("Enterprise API Gateway shutting down")


# Create gateway instance
gateway = EnterpriseAPIGateway()

# FastAPI app
app = gateway.app


@app.on_event("startup")
async def startup_event():
    await gateway.startup()


@app.on_event("shutdown")
async def shutdown_event():
    await gateway.shutdown()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
