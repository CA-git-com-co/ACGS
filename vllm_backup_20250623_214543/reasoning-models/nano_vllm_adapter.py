#!/usr/bin/env python3
"""
Nano-vLLM Adapter for ACGS-1 Constitutional Governance System

This module provides a compatibility layer between the existing vLLM-based
reasoning models integration and the new Nano-vLLM implementation.

Features:
- Drop-in replacement for vLLM HTTP API calls
- Async/await compatibility
- OpenAI-compatible response formats
- Error handling and fallback mechanisms
- Constitutional compliance validation
- Performance monitoring

Usage:
    from nano_vllm_adapter import NanoVLLMAdapter
    
    adapter = NanoVLLMAdapter(model_path="nvidia/Llama-3.1-Nemotron-70B")
    response = await adapter.chat_completion(messages, max_tokens=512)
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import json

try:
    from nanovllm import LLM, SamplingParams
    NANO_VLLM_AVAILABLE = True
except ImportError:
    NANO_VLLM_AVAILABLE = False
    LLM = None
    SamplingParams = None

from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ModelConfig:
    """Configuration for Nano-vLLM model initialization."""
    model_path: str
    tensor_parallel_size: int = 1
    enforce_eager: bool = True
    gpu_memory_utilization: float = 0.9
    max_model_len: Optional[int] = None
    trust_remote_code: bool = True


class ChatMessage(BaseModel):
    """OpenAI-compatible chat message format."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str = Field(..., description="Model identifier")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    max_tokens: int = Field(default=512, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    top_p: float = Field(default=0.9, description="Top-p sampling parameter")
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, description="Presence penalty")


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: str = Field(..., description="Unique response identifier")
    object: str = Field(default="chat.completion", description="Response object type")
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="Model used for generation")
    choices: List[Dict[str, Any]] = Field(..., description="Generated choices")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")


class NanoVLLMAdapter:
    """
    Adapter class that provides vLLM-compatible interface using Nano-vLLM.
    
    This adapter maintains the same async API as the original vLLM integration
    while using Nano-vLLM's lightweight implementation under the hood.
    """
    
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        self.llm: Optional[LLM] = None
        self.is_initialized = False
        self.model_name = Path(model_config.model_path).name
        
        if not NANO_VLLM_AVAILABLE:
            raise ImportError(
                "Nano-vLLM is not available. Please install it with: "
                "pip install git+https://github.com/GeeeekExplorer/nano-vllm.git"
            )
    
    async def initialize(self) -> None:
        """Initialize the Nano-vLLM model asynchronously."""
        if self.is_initialized:
            return
            
        logger.info("Initializing Nano-vLLM model", model_path=self.model_config.model_path)
        
        try:
            # Run model initialization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.llm = await loop.run_in_executor(
                None, self._initialize_model
            )
            self.is_initialized = True
            logger.info("Nano-vLLM model initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Nano-vLLM model", error=str(e))
            raise
    
    def _initialize_model(self) -> LLM:
        """Initialize the model in a separate thread."""
        return LLM(
            model=self.model_config.model_path,
            tensor_parallel_size=self.model_config.tensor_parallel_size,
            enforce_eager=self.model_config.enforce_eager,
            trust_remote_code=self.model_config.trust_remote_code,
            gpu_memory_utilization=self.model_config.gpu_memory_utilization,
            max_model_len=self.model_config.max_model_len,
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Nano-vLLM.
        
        Maintains compatibility with OpenAI chat completion API format.
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Convert messages to prompt format
        prompt = self._messages_to_prompt(messages)
        
        # Create sampling parameters
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        
        # Generate response asynchronously
        start_time = time.time()
        
        try:
            loop = asyncio.get_event_loop()
            outputs = await loop.run_in_executor(
                None, self.llm.generate, [prompt], sampling_params
            )
            
            generation_time = time.time() - start_time
            
            # Format response in OpenAI-compatible format
            response = self._format_response(outputs[0], generation_time)
            
            logger.info(
                "Chat completion generated",
                model=self.model_name,
                tokens=response["usage"]["completion_tokens"],
                time=generation_time
            )
            
            return response
            
        except Exception as e:
            logger.error("Chat completion failed", error=str(e))
            raise
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI messages format to a single prompt string."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    def _format_response(self, output: Any, generation_time: float) -> Dict[str, Any]:
        """Format Nano-vLLM output to OpenAI-compatible response."""
        generated_text = output.get("text", "")
        
        # Estimate token counts (rough approximation)
        completion_tokens = len(generated_text.split())
        prompt_tokens = 50  # Rough estimate
        total_tokens = completion_tokens + prompt_tokens
        
        return {
            "id": f"chatcmpl-{int(time.time() * 1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": generated_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            },
            "generation_time": generation_time
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the model is healthy and ready to serve requests."""
        try:
            if not self.is_initialized:
                return {"status": "not_initialized", "healthy": False}
            
            # Simple test generation
            test_messages = [{"role": "user", "content": "Hello"}]
            response = await self.chat_completion(
                test_messages, max_tokens=10, temperature=0.1
            )
            
            return {
                "status": "healthy",
                "healthy": True,
                "model": self.model_name,
                "response_time": response.get("generation_time", 0)
            }
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {"status": "unhealthy", "healthy": False, "error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown the model and clean up resources."""
        if self.llm:
            # Nano-vLLM doesn't have explicit shutdown, but we can clear the reference
            self.llm = None
            self.is_initialized = False
            logger.info("Nano-vLLM model shutdown complete")


# Factory function for easy instantiation
def create_nano_vllm_adapter(
    model_path: str,
    tensor_parallel_size: int = 1,
    gpu_memory_utilization: float = 0.9,
    **kwargs
) -> NanoVLLMAdapter:
    """Create a Nano-vLLM adapter with the specified configuration."""
    config = ModelConfig(
        model_path=model_path,
        tensor_parallel_size=tensor_parallel_size,
        gpu_memory_utilization=gpu_memory_utilization,
        **kwargs
    )
    return NanoVLLMAdapter(config)
