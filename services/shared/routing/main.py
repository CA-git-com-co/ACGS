"""
5-Tier Hybrid Inference Router FastAPI Application

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from hybrid_inference_router import (
    HybridInferenceRouter,
    QueryRequest,
    RoutingStrategy
)

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global router instance
router_instance = None
redis_client = None


class RouteRequest(BaseModel):
    """Request model for routing queries."""
    query: str
    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    max_tokens: int = 1000
    temperature: float = 0.7


class RouteResponse(BaseModel):
    """Response model for routing results."""
    tier: str
    model_id: str
    model_name: str
    estimated_cost: float
    estimated_latency_ms: float
    constitutional_compliance_score: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    constitutional_hash: str = CONSTITUTIONAL_HASH
    version: str = "1.0.0"
    components: Dict[str, str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global router_instance, redis_client
    
    # Startup
    logger.info("🚀 Starting 5-Tier Hybrid Inference Router")
    logger.info(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    try:
        # Initialize Redis client
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis connection established")
        
        # Initialize router
        router_instance = HybridInferenceRouter(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            redis_client=redis_client
        )
        
        logger.info("✅ 5-Tier Hybrid Inference Router initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    # Shutdown
    logger.info("🔄 Shutting down 5-Tier Hybrid Inference Router")
    
    if redis_client:
        await redis_client.close()
    
    logger.info("✅ Shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="5-Tier Hybrid Inference Router",
    description="ACGS-2 5-tier hybrid inference router with cost-optimized model selection",
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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    components = {
        "router": "healthy" if router_instance else "unhealthy",
        "redis": "healthy" if redis_client else "unhealthy"
    }
    
    # Test Redis connection
    if redis_client:
        try:
            await redis_client.ping()
            components["redis"] = "healthy"
        except:
            components["redis"] = "unhealthy"
    
    status = "healthy" if all(c == "healthy" for c in components.values()) else "unhealthy"
    
    return HealthResponse(
        status=status,
        components=components
    )


@app.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """Route a query to the optimal model tier."""
    if not router_instance:
        raise HTTPException(status_code=503, detail="Router not initialized")
    
    try:
        # Create query request
        query_request = QueryRequest(
            text=request.query,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Route the query
        result = await router_instance.route_query(
            query_request,
            strategy=request.strategy
        )
        
        return RouteResponse(
            tier=result["tier"],
            model_id=result["model_id"],
            model_name=result["model_name"],
            estimated_cost=result["estimated_cost"],
            estimated_latency_ms=result["estimated_latency_ms"],
            constitutional_compliance_score=result["constitutional_compliance_score"]
        )
        
    except Exception as e:
        logger.error(f"❌ Routing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")


@app.post("/execute")
async def execute_query(request: RouteRequest):
    """Execute a query through the router."""
    if not router_instance:
        raise HTTPException(status_code=503, detail="Router not initialized")
    
    try:
        # Create query request
        query_request = QueryRequest(
            text=request.query,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Execute the query
        result = await router_instance.execute_query(
            query_request,
            strategy=request.strategy
        )
        
        return {
            "response": result["response"],
            "tier": result["tier"],
            "model_id": result["model_id"],
            "actual_cost": result["actual_cost"],
            "actual_latency_ms": result["actual_latency_ms"],
            "constitutional_compliance_score": result["constitutional_compliance_score"],
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@app.get("/models")
async def list_models():
    """List all available models across all tiers."""
    if not router_instance:
        raise HTTPException(status_code=503, detail="Router not initialized")
    
    try:
        models = router_instance.openrouter_client.model_endpoints
        
        return {
            "total_models": len(models),
            "models_by_tier": {
                "tier_1_nano": [m for m in models.values() if m.tier.value == "tier_1_nano"],
                "tier_2_fast": [m for m in models.values() if m.tier.value == "tier_2_fast"],
                "tier_3_balanced": [m for m in models.values() if m.tier.value == "tier_3_balanced"],
                "tier_4_premium": [m for m in models.values() if m.tier.value == "tier_4_premium"],
                "tier_5_expert": [m for m in models.values() if m.tier.value == "tier_5_expert"]
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get router performance metrics."""
    if not router_instance:
        raise HTTPException(status_code=503, detail="Router not initialized")
    
    try:
        # Get metrics from Redis
        metrics = {}
        if redis_client:
            # Get routing statistics
            routing_stats = await redis_client.hgetall("router:stats")
            metrics["routing_stats"] = routing_stats
            
            # Get tier usage statistics
            tier_stats = await redis_client.hgetall("router:tier_usage")
            metrics["tier_usage"] = tier_stats
        
        return {
            "metrics": metrics,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
