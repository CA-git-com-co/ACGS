"""
NVIDIA LLM Router Server

Main entry point for the router server service.
Handles incoming LLM requests and routes them to appropriate models.
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

import aiohttp
import uvicorn
from api_key_manager import get_api_key_manager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.shared.utils import get_logger

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LLM_ROUTER_LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = get_logger(__name__)


# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str
    metadata: dict[str, Any] | None = None


class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    task_type: str | None = None
    complexity: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    stream: bool = False
    metadata: dict[str, Any] | None = None


class ChatCompletionResponse(BaseModel):
    choices: list[dict[str, Any]]
    model: str
    usage: dict[str, int] | None = None
    metadata: dict[str, Any] | None = None


# Global variables
controller_url = ""
nvidia_api_base = ""
session: aiohttp.ClientSession | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Application lifespan manager"""
    global controller_url, nvidia_api_base, session

    logger.info("Starting NVIDIA LLM Router Server")

    # Initialize configuration
    controller_url = os.getenv(
        "LLM_ROUTER_CONTROLLER_URL", "http://nvidia_llm_router_controller:8080"
    )
    nvidia_api_base = os.getenv(
        "NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1"
    )

    # Create HTTP session
    session = aiohttp.ClientSession()

    logger.info("Router Server started successfully")
    yield

    # Cleanup
    if session:
        await session.close()
    logger.info("Router Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="NVIDIA LLM Router Server",
    description="Routes LLM requests to optimal NVIDIA models",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_routing_config() -> dict[str, Any]:
    """Get routing configuration from controller"""
    try:
        async with session.get(f"{controller_url}/config") as response:
            if response.status == 200:
                return await response.json()
            logger.warning(f"Failed to get config from controller: {response.status}")
            return {}
    except Exception as e:
        logger.error(f"Error getting config from controller: {e}")
        return {}


async def select_model(request: ChatCompletionRequest) -> str:
    """Select optimal model based on request parameters"""
    # If model is explicitly specified, use it
    if request.model:
        return request.model

    # Get routing configuration
    config = await get_routing_config()

    # Task-based routing
    if request.task_type:
        task_config = config.get("task_routing", {}).get(request.task_type, {})
        preferred_models = task_config.get("preferred_models", [])
        if preferred_models:
            return preferred_models[0]  # Use first preferred model

    # Complexity-based routing
    if request.complexity:
        complexity_config = config.get("complexity_routing", {}).get(
            request.complexity, {}
        )
        preferred_tier = complexity_config.get("preferred_tier", "standard")

        # Get models from preferred tier
        tier_models = config.get("models", {}).get(preferred_tier, [])
        if tier_models:
            return tier_models[0].get("name", "nvidia/llama-3.1-8b-instruct")

    # Default fallback
    return os.getenv("FALLBACK_MODEL", "nvidia/llama-3.1-8b-instruct")


async def call_nvidia_api(
    model: str, messages: list[ChatMessage], **kwargs
) -> dict[str, Any]:
    """Call NVIDIA API with the selected model"""
    api_key_manager = get_api_key_manager()
    api_key = await api_key_manager.get_api_key_with_fallback(
        "nvidia_primary", "NVIDIA_API_KEY"
    )

    if not api_key:
        raise HTTPException(status_code=500, detail="NVIDIA API key not available")

    # Prepare request payload
    payload = {
        "model": model,
        "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
        "max_tokens": kwargs.get("max_tokens", 1024),
        "temperature": kwargs.get("temperature", 0.2),
        "stream": False,  # For now, disable streaming
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with session.post(
            f"{nvidia_api_base}/chat/completions",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status == 200:
                return await response.json()
            error_text = await response.text()
            logger.error(f"NVIDIA API error {response.status}: {error_text}")
            raise HTTPException(status_code=response.status, detail=error_text)

    except TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error calling NVIDIA API: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Health check endpoint"""
    return {"status": "healthy", "service": "nvidia-llm-router-server"}


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Main chat completions endpoint with intelligent routing"""
    start_time = time.time()

    try:
        # Select optimal model
        selected_model = await select_model(request)
        logger.info(f"Selected model: {selected_model} for task: {request.task_type}")

        # Call NVIDIA API
        response_data = await call_nvidia_api(
            model=selected_model,
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Add routing metadata
        if "metadata" not in response_data:
            response_data["metadata"] = {}

        response_data["metadata"].update(
            {
                "router_latency_ms": latency_ms,
                "selected_model": selected_model,
                "task_type": request.task_type,
                "complexity": request.complexity,
                "routing_timestamp": time.time(),
            }
        )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat completions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/v1/models")
async def list_models():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """List available models"""
    config = await get_routing_config()
    models = []

    for tier, tier_models in config.get("models", {}).items():
        for model in tier_models:
            models.append(
                {
                    "id": model.get("name", "unknown"),
                    "object": "model",
                    "tier": tier,
                    "capabilities": model.get("capabilities", []),
                    "max_tokens": model.get("max_tokens", 2048),
                }
            )

    return {"data": models}


@app.get("/metrics")
async def get_server_metrics():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Get server metrics"""
    return {
        "requests_processed": 0,  # Would be tracked in real implementation
        "average_latency_ms": 0,
        "error_rate": 0,
        "active_connections": 0,
    }


if __name__ == "__main__":
    port = int(os.getenv("LLM_ROUTER_SERVER_PORT", 8081))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("LLM_ROUTER_DEBUG_MODE", "false").lower() == "true",
        log_level=os.getenv("LLM_ROUTER_LOG_LEVEL", "info").lower(),
    )
