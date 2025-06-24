#!/usr/bin/env python3
"""
Nano-vLLM HTTP Service for ACGS-1 Constitutional Governance System

This module provides HTTP endpoints for the Nano-vLLM reasoning service,
maintaining compatibility with the original vLLM API while using the
lightweight Nano-vLLM implementation.

Features:
- FastAPI-based HTTP service
- OpenAI-compatible endpoints
- Constitutional reasoning API
- Health monitoring
- Metrics collection
- Graceful shutdown

Usage:
    python nano-vllm-service.py
    
    # Or with uvicorn directly:
    uvicorn nano-vllm-service:app --host 0.0.0.0 --port 8000
"""

import asyncio
import logging
import os
import signal
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog

# Import our Nano-vLLM components
try:
    from nano_vllm_adapter import NanoVLLMAdapter, create_nano_vllm_adapter
    ADAPTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Nano-vLLM adapter not available: {e}")
    ADAPTER_AVAILABLE = False
    NanoVLLMAdapter = None
    create_nano_vllm_adapter = None

try:
    from nano_vllm_integration import (
        NanoVLLMReasoningService,
        ReasoningRequest,
        ConstitutionalDomain,
        create_nano_vllm_reasoning_service
    )
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Nano-vLLM integration not available: {e}")
    INTEGRATION_AVAILABLE = False
    # Create dummy classes
    class NanoVLLMReasoningService:
        pass

    class ReasoningRequest:
        pass

    class ConstitutionalDomain:
        PRIVACY = "privacy"
        GOVERNANCE = "governance"
        TRANSPARENCY = "transparency"
        FAIRNESS = "fairness"
        ACCOUNTABILITY = "accountability"
        ETHICS = "ethics"

    async def create_nano_vllm_reasoning_service(*args, **kwargs):
        return None

NANO_VLLM_AVAILABLE = ADAPTER_AVAILABLE and INTEGRATION_AVAILABLE

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = structlog.get_logger(__name__)

# Global service instance
reasoning_service: Optional[NanoVLLMReasoningService] = None


# =============================================================================
# Request/Response Models
# =============================================================================

class ChatMessage(BaseModel):
    """OpenAI-compatible chat message."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str = Field(default="nano-vllm", description="Model identifier")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    max_tokens: int = Field(default=512, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    top_p: float = Field(default=0.9, description="Top-p sampling parameter")
    stream: bool = Field(default=False, description="Stream response")


class ConstitutionalReasoningRequest(BaseModel):
    """Constitutional reasoning request."""
    content: str = Field(..., description="Content to analyze")
    domain: str = Field(..., description="Constitutional domain")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    reasoning_depth: str = Field(default="standard", description="Reasoning depth")
    require_citations: bool = Field(default=True, description="Require citations")
    max_tokens: int = Field(default=2048, description="Maximum tokens")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    healthy: bool = Field(..., description="Health status")
    timestamp: float = Field(..., description="Check timestamp")
    version: str = Field(default="1.0.0", description="Service version")
    models: Dict[str, Any] = Field(default_factory=dict, description="Model status")


# =============================================================================
# Application Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global reasoning_service
    
    logger.info("Starting Nano-vLLM service...")
    
    # Initialize reasoning service
    if NANO_VLLM_AVAILABLE:
        try:
            reasoning_service = await create_nano_vllm_reasoning_service(enable_fallback=True)
            logger.info("Nano-vLLM reasoning service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize reasoning service: {e}")
            reasoning_service = None
    else:
        logger.warning("Nano-vLLM not available, service will return mock responses")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Nano-vLLM service...")
    if reasoning_service:
        await reasoning_service.shutdown()
    logger.info("Shutdown complete")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="ACGS-1 Nano-vLLM Reasoning Service",
    description="Lightweight vLLM alternative for constitutional AI reasoning",
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


# =============================================================================
# Health and Status Endpoints
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        if reasoning_service:
            health = await reasoning_service.health_check()
            return HealthResponse(
                status="healthy" if health.get("healthy", False) else "unhealthy",
                healthy=health.get("healthy", False),
                timestamp=time.time(),
                models=health.get("models", {})
            )
        else:
            return HealthResponse(
                status="no_service",
                healthy=False,
                timestamp=time.time(),
                models={}
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            healthy=False,
            timestamp=time.time(),
            models={}
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ACGS-1 Nano-vLLM Reasoning Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat_completions": "/v1/chat/completions",
            "constitutional_reasoning": "/v1/constitutional/reasoning",
            "docs": "/docs"
        }
    }


# =============================================================================
# OpenAI-Compatible Endpoints
# =============================================================================

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    try:
        if not reasoning_service:
            # Return mock response if service not available
            return {
                "id": f"chatcmpl-{int(time.time() * 1000)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"Mock response to: {request.messages[-1].content[:50]}... (Nano-vLLM service not available)"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 20,
                    "total_tokens": 70
                }
            }
        
        # Use the first available adapter for chat completion
        if reasoning_service.adapters:
            adapter = next(iter(reasoning_service.adapters.values()))
            
            # Convert messages to dict format
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            response = await adapter.chat_completion(
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p
            )
            
            return response
        else:
            raise HTTPException(status_code=503, detail="No reasoning models available")
            
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Constitutional Reasoning Endpoints
# =============================================================================

@app.post("/v1/constitutional/reasoning")
async def constitutional_reasoning(request: ConstitutionalReasoningRequest):
    """Constitutional reasoning endpoint."""
    try:
        if not reasoning_service:
            return {
                "reasoning_chain": ["Mock constitutional analysis"],
                "conclusion": "Mock conclusion for constitutional reasoning",
                "confidence_score": 0.8,
                "constitutional_compliance": {
                    "Transparency": 0.8,
                    "Fairness": 0.8,
                    "Privacy": 0.8,
                    "Accountability": 0.8
                },
                "citations": [],
                "model_used": "mock",
                "processing_time_ms": 100.0
            }
        
        # Convert domain string to enum
        try:
            domain = ConstitutionalDomain(request.domain.lower())
        except ValueError:
            domain = ConstitutionalDomain.GOVERNANCE
        
        # Create reasoning request
        reasoning_req = ReasoningRequest(
            content=request.content,
            domain=domain,
            context=request.context,
            reasoning_depth=request.reasoning_depth,
            require_citations=request.require_citations,
            max_tokens=request.max_tokens
        )
        
        # Perform reasoning
        response = await reasoning_service.constitutional_reasoning(reasoning_req)
        
        return {
            "reasoning_chain": response.reasoning_chain,
            "conclusion": response.conclusion,
            "confidence_score": response.confidence_score,
            "constitutional_compliance": response.constitutional_compliance,
            "citations": response.citations,
            "model_used": response.model_used.value,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        logger.error(f"Constitutional reasoning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/constitutional/ensemble")
async def ensemble_reasoning(request: ConstitutionalReasoningRequest):
    """Ensemble constitutional reasoning endpoint."""
    try:
        if not reasoning_service:
            raise HTTPException(status_code=503, detail="Reasoning service not available")
        
        # Convert domain string to enum
        try:
            domain = ConstitutionalDomain(request.domain.lower())
        except ValueError:
            domain = ConstitutionalDomain.GOVERNANCE
        
        # Create reasoning request
        reasoning_req = ReasoningRequest(
            content=request.content,
            domain=domain,
            context=request.context,
            reasoning_depth=request.reasoning_depth,
            require_citations=request.require_citations,
            max_tokens=request.max_tokens
        )
        
        # Perform ensemble reasoning
        response = await reasoning_service.ensemble_reasoning(reasoning_req)
        
        return {
            "reasoning_chain": response.reasoning_chain,
            "conclusion": response.conclusion,
            "confidence_score": response.confidence_score,
            "constitutional_compliance": response.constitutional_compliance,
            "citations": response.citations,
            "model_used": response.model_used.value,
            "processing_time_ms": response.processing_time_ms,
            "ensemble": True
        }
        
    except Exception as e:
        logger.error(f"Ensemble reasoning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Main Application
# =============================================================================

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    
    logger.info(f"Starting Nano-vLLM service on {host}:{port}")
    
    # Run the application
    uvicorn.run(
        "nano-vllm-service:app",
        host=host,
        port=port,
        workers=workers,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True
    )
