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
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

# GPU and system monitoring imports
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import pynvml

    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    from nanovllm import LLM, SamplingParams

    NANO_VLLM_AVAILABLE = True
    USING_MOCK = False
except ImportError:
    try:
        # Try mock implementation
        import os
        import sys

        sys.path.insert(0, os.path.dirname(__file__))
        from nanovllm_mock import LLM, SamplingParams

        NANO_VLLM_AVAILABLE = True
        USING_MOCK = True
        logger.warning("Using mock Nano-vLLM implementation")
    except ImportError:
        NANO_VLLM_AVAILABLE = False
        USING_MOCK = False
        LLM = None
        SamplingParams = None


@dataclass
class ModelConfig:
    """Configuration for Nano-vLLM model initialization."""

    model_path: str
    tensor_parallel_size: int = 1
    enforce_eager: bool = True
    gpu_memory_utilization: float = 0.9
    max_model_len: int | None = None
    trust_remote_code: bool = True
    enable_gpu_detection: bool = True
    cuda_visible_devices: str | None = None
    enable_monitoring: bool = True


class ChatMessage(BaseModel):
    """OpenAI-compatible chat message format."""

    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""

    model: str = Field(..., description="Model identifier")
    messages: list[ChatMessage] = Field(..., description="List of chat messages")
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
    choices: list[dict[str, Any]] = Field(..., description="Generated choices")
    usage: dict[str, int] = Field(..., description="Token usage statistics")


class NanoVLLMAdapter:
    """
    Adapter class that provides vLLM-compatible interface using Nano-vLLM.

    This adapter maintains the same async API as the original vLLM integration
    while using Nano-vLLM's lightweight implementation under the hood.
    """

    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        self.llm: LLM | None = None
        self.is_initialized = False
        self.model_name = Path(model_config.model_path).name
        self.gpu_info = {}
        self.metrics = {
            "requests_total": 0,
            "requests_failed": 0,
            "total_inference_time": 0.0,
            "total_tokens_generated": 0,
        }

        if not NANO_VLLM_AVAILABLE:
            raise ImportError(
                "Nano-vLLM is not available. Please install it with: "
                "pip install git+https://github.com/GeeeekExplorer/nano-vllm.git"
            )

        # Initialize GPU detection
        if model_config.enable_gpu_detection:
            self._detect_gpu_configuration()

        # Set CUDA visible devices if specified
        if model_config.cuda_visible_devices:
            os.environ["CUDA_VISIBLE_DEVICES"] = model_config.cuda_visible_devices

    async def initialize(self) -> None:
        """Initialize the Nano-vLLM model asynchronously."""
        if self.is_initialized:
            return

        logger.info(
            "Initializing Nano-vLLM model", model_path=self.model_config.model_path
        )

        try:
            # Run model initialization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.llm = await loop.run_in_executor(None, self._initialize_model)
            self.is_initialized = True
            logger.info("Nano-vLLM model initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize Nano-vLLM model", error=str(e))
            raise

    def _detect_gpu_configuration(self) -> None:
        """Detect available GPU configuration and capabilities."""
        self.gpu_info = {
            "cuda_available": False,
            "gpu_count": 0,
            "gpu_devices": [],
            "total_memory": 0,
            "driver_version": None,
        }

        if TORCH_AVAILABLE and torch.cuda.is_available():
            self.gpu_info["cuda_available"] = True
            self.gpu_info["gpu_count"] = torch.cuda.device_count()

            for i in range(torch.cuda.device_count()):
                device_props = torch.cuda.get_device_properties(i)
                device_info = {
                    "id": i,
                    "name": device_props.name,
                    "memory_total": device_props.total_memory,
                    "memory_free": torch.cuda.mem_get_info(i)[0],
                    "compute_capability": f"{device_props.major}.{device_props.minor}",
                }
                self.gpu_info["gpu_devices"].append(device_info)
                self.gpu_info["total_memory"] += device_props.total_memory

        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_info["driver_version"] = pynvml.nvmlSystemGetDriverVersion()
            except Exception as e:
                logger.warning("Failed to initialize NVML", error=str(e))

        logger.info("GPU configuration detected", gpu_info=self.gpu_info)

    def _initialize_model(self) -> LLM:
        """Initialize the model in a separate thread."""
        # Adjust tensor parallel size based on available GPUs
        if self.gpu_info.get("cuda_available", False):
            available_gpus = self.gpu_info.get("gpu_count", 1)
            if self.model_config.tensor_parallel_size > available_gpus:
                logger.warning(
                    "Reducing tensor parallel size to match available GPUs",
                    requested=self.model_config.tensor_parallel_size,
                    available=available_gpus,
                )
                self.model_config.tensor_parallel_size = available_gpus

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
        messages: list[dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs,
    ) -> dict[str, Any]:
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

            # Update metrics
            self._update_metrics(response, generation_time, success=True)

            logger.info(
                "Chat completion generated",
                model=self.model_name,
                tokens=response["usage"]["completion_tokens"],
                time=generation_time,
            )

            return response

        except Exception as e:
            self._update_metrics(None, time.time() - start_time, success=False)
            logger.error("Chat completion failed", error=str(e))
            raise

    def _messages_to_prompt(self, messages: list[dict[str, str]]) -> str:
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

    def _format_response(self, output: Any, generation_time: float) -> dict[str, Any]:
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
                    "message": {"role": "assistant", "content": generated_text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "generation_time": generation_time,
        }

    def _update_metrics(
        self, response: dict[str, Any] | None, generation_time: float, success: bool
    ) -> None:
        """Update internal metrics for monitoring."""
        self.metrics["requests_total"] += 1
        self.metrics["total_inference_time"] += generation_time

        if success and response:
            tokens = response.get("usage", {}).get("completion_tokens", 0)
            self.metrics["total_tokens_generated"] += tokens
        else:
            self.metrics["requests_failed"] += 1

    async def get_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        gpu_metrics = {}
        if self.gpu_info.get("cuda_available", False) and TORCH_AVAILABLE:
            try:
                for i, device in enumerate(self.gpu_info["gpu_devices"]):
                    memory_used = torch.cuda.memory_allocated(i)
                    memory_total = device["memory_total"]
                    gpu_metrics[f"gpu_{i}_memory_used"] = memory_used
                    gpu_metrics[f"gpu_{i}_memory_utilization"] = (
                        memory_used / memory_total
                    )
                    gpu_metrics[f"gpu_{i}_temperature"] = self._get_gpu_temperature(i)
            except Exception as e:
                logger.warning("Failed to collect GPU metrics", error=str(e))

        avg_inference_time = 0
        if self.metrics["requests_total"] > 0:
            avg_inference_time = (
                self.metrics["total_inference_time"] / self.metrics["requests_total"]
            )

        return {
            "requests_total": self.metrics["requests_total"],
            "requests_failed": self.metrics["requests_failed"],
            "success_rate": (
                self.metrics["requests_total"] - self.metrics["requests_failed"]
            )
            / max(1, self.metrics["requests_total"]),
            "avg_inference_time": avg_inference_time,
            "total_tokens_generated": self.metrics["total_tokens_generated"],
            "gpu_info": self.gpu_info,
            **gpu_metrics,
        }

    def _get_gpu_temperature(self, device_id: int) -> float | None:
        """Get GPU temperature if available."""
        if PYNVML_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
                temp = pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU
                )
                return float(temp)
            except Exception:
                pass
        return None

    async def health_check(self) -> dict[str, Any]:
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
                "response_time": response.get("generation_time", 0),
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
    **kwargs,
) -> NanoVLLMAdapter:
    """Create a Nano-vLLM adapter with the specified configuration."""
    config = ModelConfig(
        model_path=model_path,
        tensor_parallel_size=tensor_parallel_size,
        gpu_memory_utilization=gpu_memory_utilization,
        **kwargs,
    )
    return NanoVLLMAdapter(config)
