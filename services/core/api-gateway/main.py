"""
API Gateway Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service providing API gateway functionality with rate limiting,
authentication, authorization, and traffic management for all ACGS-2 services.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import httpx
import os
import json
import time
from collections import defaultdict, deque
import hashlib
import jwt
from functools import wraps

from .models import (
    RateLimitRule, APIPolicy, TrafficMetrics, GatewayConfig,
    ServiceRoute, RateLimitBucket, AuthPolicy, CachePolicy,
    RequestLog, SecurityPolicy, LoadBalancingPolicy, CircuitBreakerState,
    CONSTITUTIONAL_HASH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service routes - maps endpoints to backend services
SERVICE_ROUTES = {
    "/api/v1/auth": {
        "service": "auth-service",
        "url": "http://localhost:8013",
        "timeout": 10.0,
        "auth_required": False
    },
    "/api/v1/constitutional": {
        "service": "constitutional-core", 
        "url": "http://localhost:8001",
        "timeout": 15.0,
        "auth_required": True
    },
    "/api/v1/groq": {
        "service": "groqcloud-policy",
        "url": "http://localhost:8023", 
        "timeout": 30.0,
        "auth_required": True
    },
    "/api/v1/agents": {
        "service": "multi-agent-coordination",
        "url": "http://localhost:8008",
        "timeout": 20.0,
        "auth_required": True
    },
    "/api/v1/workers": {
        "service": "worker-agents",
        "url": "http://localhost:8009",
        "timeout": 15.0,
        "auth_required": True
    },
    "/api/v1/blackboard": {
        "service": "blackboard-coordination",
        "url": "http://localhost:8010",
        "timeout": 15.0,
        "auth_required": True
    },
    "/api/v1/mcp": {
        "service": "mcp-aggregator",
        "url": "http://localhost:3000",
        "timeout": 20.0,
        "auth_required": True
    },
    "/api/v1/a2a": {
        "service": "a2a-policy",
        "url": "http://localhost:8020",
        "timeout": 15.0,
        "auth_required": True
    },
    "/api/v1/security": {
        "service": "security-validation",
        "url": "http://localhost:8021",
        "timeout": 10.0,
        "auth_required": True
    },
    "/api/v1/consensus": {
        "service": "consensus-engine",
        "url": "http://localhost:8011",
        "timeout": 25.0,
        "auth_required": True
    },
    "/api/v1/hitl": {
        "service": "human-in-the-loop",
        "url": "http://localhost:8012",
        "timeout": 20.0,
        "auth_required": True
    },
    "/api/v1/monitoring": {
        "service": "monitoring-service",
        "url": "http://localhost:8014",
        "timeout": 10.0,
        "auth_required": True
    },
    "/api/v1/audit": {
        "service": "audit-service",
        "url": "http://localhost:8015",
        "timeout": 15.0,
        "auth_required": True
    },
    "/api/v1/gdpr": {
        "service": "gdpr-compliance",
        "url": "http://localhost:8016",
        "timeout": 20.0,
        "auth_required": True
    },
    "/api/v1/alerts": {
        "service": "alerting-service",
        "url": "http://localhost:8017",
        "timeout": 15.0,
        "auth_required": True
    }
}

# Global storage
gateway_storage = {
    "rate_limits": defaultdict(lambda: defaultdict(deque)),  # client_id -> endpoint -> request_times
    "policies": {},
    "metrics": defaultdict(int),
    "request_logs": deque(maxlen=10000),
    "circuit_breakers": {},
    "cache": {},
    "blocked_ips": set(),
    "api_keys": {}
}

# Configuration
GATEWAY_CONFIG = {
    "default_rate_limit": 100,  # requests per minute
    "burst_limit": 10,  # additional requests allowed in burst
    "auth_service_url": "http://localhost:8013",
    "jwt_secret": os.getenv("JWT_SECRET", "acgs_jwt_secret_key"),
    "cache_ttl_seconds": 300,  # 5 minutes
    "circuit_breaker_threshold": 5,  # failures before opening circuit
    "circuit_breaker_timeout": 60,  # seconds before attempting reset
    "enable_caching": True,
    "enable_rate_limiting": True,
    "enable_circuit_breaker": True
}

# HTTP client for backend requests
http_client = httpx.AsyncClient(timeout=30.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting API Gateway Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize gateway policies
    await initialize_default_policies()
    await initialize_circuit_breakers()
    
    # Start background tasks
    asyncio.create_task(cleanup_rate_limit_data())
    asyncio.create_task(monitor_circuit_breakers())
    asyncio.create_task(cache_cleanup())
    asyncio.create_task(collect_metrics())
    
    yield
    
    # Cleanup
    await http_client.aclose()
    logger.info("Shutting down API Gateway Service")

app = FastAPI(
    title="API Gateway Service",
    description="Central API gateway for ACGS-2 services",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        if not GATEWAY_CONFIG["enable_rate_limiting"]:
            return await call_next(request)
        
        client_ip = request.client.host
        endpoint = request.url.path
        
        # Check rate limit
        if await is_rate_limited(client_ip, endpoint):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
            )
        
        return await call_next(request)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware"""
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        # Check if IP is blocked
        if client_ip in gateway_storage["blocked_ips"]:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Access denied",
                    "message": "Your IP address has been blocked",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
            )
        
        # Log request
        await log_request(request)
        
        return await call_next(request)

# Add middlewares
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

async def initialize_default_policies():
    """Initialize default gateway policies"""
    
    # Rate limiting policies
    rate_limit_policies = [
        RateLimitRule(
            name="Authentication Endpoints",
            pattern="/api/v1/auth/*",
            requests_per_minute=20,
            burst_allowance=5,
            description="Rate limit for authentication endpoints"
        ),
        RateLimitRule(
            name="Constitutional Operations",
            pattern="/api/v1/constitutional/*",
            requests_per_minute=50,
            burst_allowance=10,
            description="Rate limit for constitutional operations"
        ),
        RateLimitRule(
            name="General API",
            pattern="/api/v1/*",
            requests_per_minute=100,
            burst_allowance=20,
            description="Default rate limit for API endpoints"
        ),
        RateLimitRule(
            name="Health Checks",
            pattern="*/health",
            requests_per_minute=300,
            burst_allowance=50,
            description="Rate limit for health check endpoints"
        )
    ]
    
    for policy in rate_limit_policies:
        gateway_storage["policies"][policy.rule_id] = policy
    
    # Security policies
    security_policy = SecurityPolicy(
        name="Default Security Policy",
        block_suspicious_ips=True,
        require_https=False,  # Allow HTTP for local development
        constitutional_hash_validation=True,
        max_request_size_mb=10,
        allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        blocked_user_agents=["bot", "crawler", "spider"],
        rate_limit_violations_before_block=10
    )
    
    gateway_storage["policies"]["security_default"] = security_policy
    
    logger.info(f"Initialized {len(rate_limit_policies)} rate limit policies")

async def initialize_circuit_breakers():
    """Initialize circuit breakers for backend services"""
    for route_pattern, config in SERVICE_ROUTES.items():
        service_name = config["service"]
        
        circuit_breaker = CircuitBreakerState(
            service_name=service_name,
            failure_threshold=GATEWAY_CONFIG["circuit_breaker_threshold"],
            timeout_seconds=GATEWAY_CONFIG["circuit_breaker_timeout"],
            state="closed"
        )
        
        gateway_storage["circuit_breakers"][service_name] = circuit_breaker
    
    logger.info(f"Initialized circuit breakers for {len(SERVICE_ROUTES)} services")

async def is_rate_limited(client_ip: str, endpoint: str) -> bool:
    """Check if client is rate limited"""
    current_time = time.time()
    
    # Find applicable rate limit rule
    rate_limit = GATEWAY_CONFIG["default_rate_limit"]
    burst_limit = GATEWAY_CONFIG["burst_limit"]
    
    for policy in gateway_storage["policies"].values():
        if isinstance(policy, RateLimitRule) and matches_pattern(endpoint, policy.pattern):
            rate_limit = policy.requests_per_minute
            burst_limit = policy.burst_allowance
            break
    
    # Check rate limit
    request_times = gateway_storage["rate_limits"][client_ip][endpoint]
    
    # Remove old requests (outside the minute window)
    while request_times and request_times[0] < current_time - 60:
        request_times.popleft()
    
    # Check if over limit
    if len(request_times) >= rate_limit + burst_limit:
        gateway_storage["metrics"]["rate_limit_violations"] += 1
        return True
    
    # Add current request
    request_times.append(current_time)
    return False

def matches_pattern(path: str, pattern: str) -> bool:
    """Check if path matches pattern (supports wildcards)"""
    if pattern.endswith("*"):
        return path.startswith(pattern[:-1])
    return path == pattern

async def log_request(request: Request):
    """Log incoming request"""
    log_entry = RequestLog(
        client_ip=request.client.host,
        method=request.method,
        path=request.url.path,
        user_agent=request.headers.get("user-agent", ""),
        timestamp=datetime.utcnow()
    )
    
    gateway_storage["request_logs"].append(log_entry)
    gateway_storage["metrics"]["total_requests"] += 1

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token, 
            GATEWAY_CONFIG["jwt_secret"], 
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from request"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return await verify_token(token)

async def check_circuit_breaker(service_name: str) -> bool:
    """Check if circuit breaker allows request"""
    if not GATEWAY_CONFIG["enable_circuit_breaker"]:
        return True
    
    circuit_breaker = gateway_storage["circuit_breakers"].get(service_name)
    if not circuit_breaker:
        return True
    
    current_time = time.time()
    
    if circuit_breaker.state == "open":
        # Check if timeout has passed
        if current_time - circuit_breaker.last_failure_time > circuit_breaker.timeout_seconds:
            circuit_breaker.state = "half_open"
            logger.info(f"Circuit breaker for {service_name} moved to half-open")
        else:
            return False
    
    return True

async def record_service_result(service_name: str, success: bool):
    """Record service call result for circuit breaker"""
    circuit_breaker = gateway_storage["circuit_breakers"].get(service_name)
    if not circuit_breaker:
        return
    
    current_time = time.time()
    
    if success:
        circuit_breaker.consecutive_failures = 0
        if circuit_breaker.state == "half_open":
            circuit_breaker.state = "closed"
            logger.info(f"Circuit breaker for {service_name} closed")
    else:
        circuit_breaker.consecutive_failures += 1
        circuit_breaker.last_failure_time = current_time
        
        if circuit_breaker.consecutive_failures >= circuit_breaker.failure_threshold:
            circuit_breaker.state = "open"
            logger.warning(f"Circuit breaker for {service_name} opened")

async def proxy_request(request: Request, service_config: Dict[str, Any]) -> Response:
    """Proxy request to backend service"""
    service_name = service_config["service"]
    base_url = service_config["url"]
    timeout = service_config.get("timeout", 10.0)
    
    # Check circuit breaker
    if not await check_circuit_breaker(service_name):
        gateway_storage["metrics"]["circuit_breaker_blocks"] += 1
        raise HTTPException(
            status_code=503,
            detail=f"Service {service_name} is temporarily unavailable"
        )
    
    # Build target URL
    path = request.url.path
    query_string = str(request.url.query)
    target_url = f"{base_url}{path}"
    if query_string:
        target_url += f"?{query_string}"
    
    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    try:
        # Make request to backend
        start_time = time.time()
        
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            timeout=timeout
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Record success
        await record_service_result(service_name, True)
        
        # Update metrics
        gateway_storage["metrics"]["successful_requests"] += 1
        gateway_storage["metrics"][f"service_{service_name}_requests"] += 1
        gateway_storage["metrics"][f"service_{service_name}_response_time"] = response_time
        
        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
        
    except httpx.TimeoutException:
        await record_service_result(service_name, False)
        gateway_storage["metrics"]["timeout_errors"] += 1
        raise HTTPException(
            status_code=504,
            detail=f"Service {service_name} request timeout"
        )
    
    except httpx.ConnectError:
        await record_service_result(service_name, False)
        gateway_storage["metrics"]["connection_errors"] += 1
        raise HTTPException(
            status_code=503,
            detail=f"Service {service_name} is unavailable"
        )
    
    except Exception as e:
        await record_service_result(service_name, False)
        gateway_storage["metrics"]["unknown_errors"] += 1
        logger.error(f"Error proxying to {service_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal gateway error"
        )

async def cleanup_rate_limit_data():
    """Clean up old rate limit data"""
    while True:
        try:
            current_time = time.time()
            cutoff_time = current_time - 3600  # Remove data older than 1 hour
            
            for client_ip in list(gateway_storage["rate_limits"].keys()):
                for endpoint in list(gateway_storage["rate_limits"][client_ip].keys()):
                    request_times = gateway_storage["rate_limits"][client_ip][endpoint]
                    
                    # Remove old entries
                    while request_times and request_times[0] < cutoff_time:
                        request_times.popleft()
                    
                    # Remove empty queues
                    if not request_times:
                        del gateway_storage["rate_limits"][client_ip][endpoint]
                
                # Remove empty client entries
                if not gateway_storage["rate_limits"][client_ip]:
                    del gateway_storage["rate_limits"][client_ip]
            
            await asyncio.sleep(300)  # Clean every 5 minutes
            
        except Exception as e:
            logger.error(f"Rate limit cleanup error: {e}")
            await asyncio.sleep(300)

async def monitor_circuit_breakers():
    """Monitor circuit breaker states"""
    while True:
        try:
            # Log circuit breaker states
            open_breakers = [
                name for name, cb in gateway_storage["circuit_breakers"].items()
                if cb.state == "open"
            ]
            
            if open_breakers:
                logger.warning(f"Open circuit breakers: {open_breakers}")
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Circuit breaker monitoring error: {e}")
            await asyncio.sleep(60)

async def cache_cleanup():
    """Clean up expired cache entries"""
    while True:
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, (value, timestamp) in gateway_storage["cache"].items():
                if current_time - timestamp > GATEWAY_CONFIG["cache_ttl_seconds"]:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del gateway_storage["cache"][key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            await asyncio.sleep(300)  # Clean every 5 minutes
            
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            await asyncio.sleep(300)

async def collect_metrics():
    """Collect gateway metrics"""
    while True:
        try:
            # Update circuit breaker metrics
            for name, cb in gateway_storage["circuit_breakers"].items():
                gateway_storage["metrics"][f"circuit_breaker_{name}_state"] = cb.state
                gateway_storage["metrics"][f"circuit_breaker_{name}_failures"] = cb.consecutive_failures
            
            # Update rate limit metrics
            active_limits = sum(
                len(endpoints) for endpoints in gateway_storage["rate_limits"].values()
            )
            gateway_storage["metrics"]["active_rate_limits"] = active_limits
            
            await asyncio.sleep(60)  # Collect every minute
            
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            await asyncio.sleep(60)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "gateway_stats": {
            "total_requests": gateway_storage["metrics"]["total_requests"],
            "successful_requests": gateway_storage["metrics"]["successful_requests"],
            "rate_limit_violations": gateway_storage["metrics"]["rate_limit_violations"],
            "circuit_breaker_blocks": gateway_storage["metrics"]["circuit_breaker_blocks"],
            "active_routes": len(SERVICE_ROUTES),
            "active_policies": len(gateway_storage["policies"])
        }
    }

@app.get("/gateway/metrics")
async def get_gateway_metrics():
    """Get detailed gateway metrics"""
    return {
        "metrics": dict(gateway_storage["metrics"]),
        "circuit_breakers": {
            name: {
                "state": cb.state,
                "consecutive_failures": cb.consecutive_failures,
                "last_failure_time": cb.last_failure_time
            }
            for name, cb in gateway_storage["circuit_breakers"].items()
        },
        "rate_limit_stats": {
            "active_clients": len(gateway_storage["rate_limits"]),
            "total_endpoints_tracked": sum(
                len(endpoints) for endpoints in gateway_storage["rate_limits"].values()
            )
        },
        "cache_stats": {
            "total_entries": len(gateway_storage["cache"]),
            "cache_enabled": GATEWAY_CONFIG["enable_caching"]
        }
    }

@app.get("/gateway/routes")
async def list_routes():
    """List available routes"""
    return {
        "routes": SERVICE_ROUTES,
        "total_routes": len(SERVICE_ROUTES)
    }

@app.get("/gateway/policies")
async def list_policies():
    """List gateway policies"""
    policies = {}
    for policy_id, policy in gateway_storage["policies"].items():
        if hasattr(policy, 'dict'):
            policies[policy_id] = policy.dict()
        else:
            policies[policy_id] = str(policy)
    
    return {
        "policies": policies,
        "total_policies": len(gateway_storage["policies"])
    }

# Route all API requests through the gateway
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def gateway_proxy(request: Request, path: str):
    """Main gateway proxy handler"""
    full_path = f"/api/{path}"
    
    # Find matching route
    service_config = None
    for route_pattern, config in SERVICE_ROUTES.items():
        if full_path.startswith(route_pattern):
            service_config = config
            break
    
    if not service_config:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    
    # Check authentication if required
    if service_config.get("auth_required", False):
        user = await get_current_user(request)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
    
    # Proxy the request
    return await proxy_request(request, service_config)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)