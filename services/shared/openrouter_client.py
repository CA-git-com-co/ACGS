#!/usr/bin/env python3
"""
OpenRouter API Client for ACGS-1 Phase 2 Enhanced Multi-Model Integration

This module provides a robust OpenRouter API client with proper error handling,
retry logic, and integration with the ACGS-1 constitutional governance system.

Key Features:
- Async API client with timeout and retry handling
- Support for DeepSeek Chat v3, DeepSeek R1, and Qwen3-235B models
- Constitutional hash validation integration
- Performance monitoring and metrics collection
- Proper error handling and fallback mechanisms
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import aiohttp
import structlog

from .langgraph_config import get_langgraph_config

logger = structlog.get_logger(__name__)


@dataclass
class OpenRouterResponse:
    """Response from OpenRouter API."""

    content: str
    model: str
    usage: Dict[str, int]
    response_time_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OpenRouterRequest:
    """Request to OpenRouter API."""

    model: str
    messages: List[Dict[str, str]]
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: float = 30.0
    extra_headers: Optional[Dict[str, str]] = None


class OpenRouterClient:
    """
    Enhanced OpenRouter API client for Phase 2 multi-model integration.

    Provides robust API interactions with proper error handling, retry logic,
    and integration with ACGS-1 constitutional governance requirements.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenRouter client."""
        self.config = get_langgraph_config()
        self.api_key = api_key or self.config.openrouter_api_key

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        self.base_url = "https://openrouter.ai/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None

        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0

        # Supported models for Phase 2
        self.supported_models = {
            "deepseek_chat_v3": "deepseek/deepseek-chat-v3-0324:free",
            "deepseek_r1": "deepseek/deepseek-r1",
            "qwen3_235b": "qwen/qwen3-235b-a22b:free",
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def initialize(self):
        """Initialize the HTTP session."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=60.0)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("OpenRouter client initialized")

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("OpenRouter client closed")

    def _get_default_headers(
        self, extra_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Get default headers for OpenRouter API requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://acgs.ai",
            "X-Title": "ACGS-1 Constitutional Governance System",
            "Content-Type": "application/json",
        }

        if extra_headers:
            headers.update(extra_headers)

        return headers

    async def chat_completion(self, request: OpenRouterRequest) -> OpenRouterResponse:
        """
        Send chat completion request to OpenRouter API.

        Args:
            request: OpenRouter request configuration

        Returns:
            OpenRouter response with content and metadata
        """
        if not self.session:
            await self.initialize()

        start_time = time.time()
        self.total_requests += 1

        try:
            # Prepare request payload
            payload = {
                "model": request.model,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": False,
            }

            headers = self._get_default_headers(request.extra_headers)

            # Make API request with retry logic
            response_data = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=request.timeout,
            )

            # Parse response
            if "choices" in response_data and response_data["choices"]:
                content = response_data["choices"][0]["message"]["content"]
                usage = response_data.get("usage", {})

                response_time = (time.time() - start_time) * 1000
                self.successful_requests += 1
                self.total_response_time += response_time

                logger.info(
                    "OpenRouter API request successful",
                    model=request.model,
                    response_time_ms=response_time,
                    tokens_used=usage.get("total_tokens", 0),
                )

                return OpenRouterResponse(
                    content=content,
                    model=request.model,
                    usage=usage,
                    response_time_ms=response_time,
                    success=True,
                    metadata={
                        "request_id": response_data.get("id"),
                        "created": response_data.get("created"),
                        "provider": response_data.get("provider", {}),
                    },
                )
            else:
                raise ValueError("Invalid response format from OpenRouter API")

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.failed_requests += 1

            logger.error(
                "OpenRouter API request failed",
                model=request.model,
                error=str(e),
                response_time_ms=response_time,
            )

            return OpenRouterResponse(
                content="",
                model=request.model,
                usage={},
                response_time_ms=response_time,
                success=False,
                error=str(e),
            )

    async def _make_request_with_retry(
        self, method: str, url: str, max_retries: int = 3, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with exponential backoff retry logic."""

        for attempt in range(max_retries + 1):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limit
                        if attempt < max_retries:
                            wait_time = 2**attempt
                            logger.warning(
                                f"Rate limited, retrying in {wait_time}s",
                                attempt=attempt + 1,
                                max_retries=max_retries,
                            )
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message="Rate limit exceeded",
                            )
                    else:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status}: {error_text}",
                        )

            except asyncio.TimeoutError:
                if attempt < max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        f"Request timeout, retrying in {wait_time}s",
                        attempt=attempt + 1,
                        max_retries=max_retries,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        f"Request failed: {e}, retrying in {wait_time}s",
                        attempt=attempt + 1,
                        max_retries=max_retries,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise

        raise Exception("Max retries exceeded")

    def get_model_id(self, model_name: str) -> str:
        """Get OpenRouter model ID from friendly name."""
        return self.supported_models.get(model_name, model_name)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics."""
        success_rate = (self.successful_requests / max(1, self.total_requests)) * 100
        avg_response_time = self.total_response_time / max(1, self.successful_requests)

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate_percentage": success_rate,
            "average_response_time_ms": avg_response_time,
            "supported_models": list(self.supported_models.keys()),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of OpenRouter API connectivity."""
        try:
            test_request = OpenRouterRequest(
                model=self.supported_models["deepseek_chat_v3"],
                messages=[{"role": "user", "content": "Test connectivity"}],
                temperature=0.1,
                max_tokens=10,
                timeout=10.0,
            )

            response = await self.chat_completion(test_request)

            return {
                "status": "healthy" if response.success else "unhealthy",
                "api_accessible": response.success,
                "response_time_ms": response.response_time_ms,
                "error": response.error,
                "metrics": self.get_performance_metrics(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "metrics": self.get_performance_metrics(),
            }


# Global client instance
_openrouter_client: Optional[OpenRouterClient] = None


async def get_openrouter_client() -> OpenRouterClient:
    """Get global OpenRouter client instance."""
    global _openrouter_client

    if _openrouter_client is None:
        _openrouter_client = OpenRouterClient()
        await _openrouter_client.initialize()

    return _openrouter_client


async def close_openrouter_client():
    """Close global OpenRouter client instance."""
    global _openrouter_client

    if _openrouter_client:
        await _openrouter_client.close()
        _openrouter_client = None
