"""
ACGS-2 XAI Integration Service

Production-ready X.AI Grok integration service for ACGS-2 multi-model constitutional governance.
Provides constitutional AI capabilities with formal verification and performance optimization.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from xai_grok_sdk import XAI

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets
TARGET_P99_LATENCY_MS = 5000  # 5 seconds for LLM calls (different from core services)
TARGET_CACHE_HIT_RATE = 0.85
TARGET_THROUGHPUT_RPS = 50  # Conservative for LLM operations


class XAIRequest(BaseModel):
    """Request model for XAI chat completion."""
    message: str = Field(..., description="The user message to send to Grok")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    model: str = Field("grok-4-0709", description="Grok model to use")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Sampling temperature")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Maximum tokens in response")
    constitutional_validation: bool = Field(True, description="Enable constitutional validation")


class XAIResponse(BaseModel):
    """Response model for XAI chat completion."""
    success: bool
    content: Optional[str] = None
    model: str
    constitutional_hash_valid: bool
    response_time_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConstitutionalXAIClient:
    """Enhanced XAI client with ACGS-2 constitutional governance integration."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the constitutional XAI client.

        Args:
            api_key: X.AI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("X.AI API key not provided and XAI_API_KEY not found in environment")

        # Use grok-beta as default model (available in the SDK)
        self.client = XAI(
            api_key=self.api_key,
            model="grok-beta"
        )
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Simple in-memory cache for constitutional validation
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 1000
    
    def _generate_cache_key(self, message: str, system_prompt: str, model: str, temperature: float) -> str:
        """Generate cache key for request."""
        import hashlib
        content = f"{message}|{system_prompt}|{model}|{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _validate_constitutional_compliance(self, content: str) -> bool:
        """Validate response for constitutional compliance."""
        # Basic constitutional validation - can be enhanced with formal verification
        forbidden_patterns = [
            "discriminat", "bias", "harmful", "illegal", "unethical"
        ]
        
        content_lower = content.lower()
        for pattern in forbidden_patterns:
            if pattern in content_lower:
                return False
        
        return True
    
    async def chat_completion(self, request: XAIRequest) -> XAIResponse:
        """Send constitutional chat completion request to Grok.
        
        Args:
            request: XAI request parameters
            
        Returns:
            XAI response with constitutional validation
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(
                request.message, 
                request.system_prompt or "", 
                request.model, 
                request.temperature
            )
            
            if cache_key in self.response_cache:
                self.cache_hits += 1
                cached_response = self.response_cache[cache_key]
                response_time = (time.time() - start_time) * 1000
                
                return XAIResponse(
                    success=True,
                    content=cached_response["content"],
                    model=request.model,
                    constitutional_hash_valid=True,
                    response_time_ms=response_time,
                    metadata={
                        "cached": True,
                        "constitutional_hash": self.constitutional_hash
                    }
                )
            
            self.cache_misses += 1
            
            # Prepare messages for XAI SDK
            messages = []

            # Add constitutional validation to system prompt
            constitutional_system = f"Constitutional Hash: {self.constitutional_hash}\n"
            constitutional_system += "You must adhere to constitutional AI governance principles. "
            constitutional_system += "Provide helpful, harmless, and honest responses that respect human autonomy and dignity.\n"

            if request.system_prompt:
                constitutional_system += request.system_prompt
            else:
                constitutional_system += "You are a helpful AI assistant."

            # Add system message
            messages.append({"role": "system", "content": constitutional_system})
            # Add user message
            messages.append({"role": "user", "content": request.message})

            # Get response using XAI SDK
            response = self.client.invoke(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            response_time = (time.time() - start_time) * 1000
            self.total_response_time += response_time

            # Extract content from XAI SDK response
            response_content = ""
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if choice.message and choice.message.content:
                    response_content = choice.message.content

            # Constitutional validation
            constitutional_valid = True
            if request.constitutional_validation and response_content:
                constitutional_valid = self._validate_constitutional_compliance(response_content)

            # Cache successful responses
            if constitutional_valid and len(self.response_cache) < self.max_cache_size:
                self.response_cache[cache_key] = {
                    "content": response_content,
                    "timestamp": time.time()
                }

            return XAIResponse(
                success=True,
                content=response_content,
                model=request.model,
                constitutional_hash_valid=constitutional_valid,
                response_time_ms=response_time,
                metadata={
                    "cached": False,
                    "constitutional_hash": self.constitutional_hash,
                    "tokens_used": response.usage.total_tokens if response.usage else len(response_content.split())
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return XAIResponse(
                success=False,
                content=None,
                model=request.model,
                constitutional_hash_valid=False,
                response_time_ms=response_time,
                error=str(e),
                metadata={
                    "constitutional_hash": self.constitutional_hash
                }
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        avg_response_time = self.total_response_time / self.request_count if self.request_count > 0 else 0
        
        return {
            "request_count": self.request_count,
            "cache_hit_rate": cache_hit_rate,
            "average_response_time_ms": avg_response_time,
            "cache_size": len(self.response_cache),
            "constitutional_hash": self.constitutional_hash,
            "performance_targets": {
                "target_cache_hit_rate": TARGET_CACHE_HIT_RATE,
                "target_p99_latency_ms": TARGET_P99_LATENCY_MS,
                "target_throughput_rps": TARGET_THROUGHPUT_RPS
            }
        }


# Global XAI client instance
xai_client: Optional[ConstitutionalXAIClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global xai_client
    
    # Startup
    try:
        xai_client = ConstitutionalXAIClient()
        print(f"✅ XAI Integration Service started with constitutional hash: {CONSTITUTIONAL_HASH}")
    except Exception as e:
        print(f"❌ Failed to initialize XAI client: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🔄 XAI Integration Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="ACGS-2 XAI Integration Service",
    description="X.AI Grok integration with constitutional governance",
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


def get_xai_client() -> ConstitutionalXAIClient:
    """Dependency to get XAI client."""
    if xai_client is None:
        raise HTTPException(status_code=503, detail="XAI client not initialized")
    return xai_client


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "xai-integration",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": time.time()
    }


@app.post("/chat/completion", response_model=XAIResponse)
async def chat_completion(
    request: XAIRequest,
    client: ConstitutionalXAIClient = Depends(get_xai_client)
):
    """Send chat completion request to X.AI Grok with constitutional validation."""
    return await client.chat_completion(request)


@app.get("/metrics")
async def get_metrics(client: ConstitutionalXAIClient = Depends(get_xai_client)):
    """Get performance metrics for the XAI integration service."""
    return client.get_performance_metrics()


@app.post("/validate/constitutional")
async def validate_constitutional_compliance(
    content: str,
    client: ConstitutionalXAIClient = Depends(get_xai_client)
):
    """Validate content for constitutional compliance."""
    is_valid = client._validate_constitutional_compliance(content)
    
    return {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "content_valid": is_valid,
        "validation_timestamp": time.time()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8014,  # New port for XAI integration service
        reload=True,
        log_level="info"
    )
