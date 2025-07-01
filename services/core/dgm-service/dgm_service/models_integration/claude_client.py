"""
Claude 3.5 Sonnet client implementation.
"""

import json
import logging
import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .model_client import (
    AuthenticationError,
    ModelClient,
    ModelClientError,
    ModelRequest,
    ModelResponse,
    ModelUnavailableError,
    RateLimitError,
    TokenLimitError,
)

logger = logging.getLogger(__name__)


class ClaudeClient(ModelClient):
    """
    Claude 3.5 Sonnet client for Anthropic API.

    Provides secure integration with Claude models including
    rate limiting, retries, and error handling.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "claude-3-5-sonnet-20241022",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_requests: int = 50,  # Conservative rate limit
        rate_limit_window: int = 60,
    ):
        super().__init__(
            api_key=api_key,
            model_name=model_name,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=rate_limit_window,
        )

        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Claude-specific pricing (per 1K tokens)
        self.input_cost_per_1k = 0.003  # $0.003 per 1K input tokens
        self.output_cost_per_1k = 0.015  # $0.015 per 1K output tokens

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response from Claude."""
        start_time = time.time()

        try:
            # Validate request
            self._validate_request(request)

            # Check circuit breaker
            self._check_circuit_breaker()

            # Check rate limit
            await self._check_rate_limit()

            # Prepare request payload
            payload = self._prepare_payload(request)

            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/messages", headers=self.headers, json=payload
                )

                # Handle response
                if response.status_code == 200:
                    result = response.json()
                    model_response = self._parse_response(result, start_time)

                    # Update usage tracking
                    self._update_usage(model_response.usage)
                    self._record_success()

                    return model_response

                await self._handle_error_response(response)

        except Exception as e:
            self._record_failure()
            logger.error(f"Claude API request failed: {e}")
            raise

    async def generate_stream(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response from Claude."""
        try:
            # Validate request
            self._validate_request(request)

            # Check circuit breaker
            self._check_circuit_breaker()

            # Check rate limit
            await self._check_rate_limit()

            # Prepare request payload with streaming
            payload = self._prepare_payload(request)
            payload["stream"] = True

            # Make streaming API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        await self._handle_error_response(response)

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix

                            if data == "[DONE]":
                                break

                            try:
                                chunk = json.loads(data)
                                if chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    if "text" in delta:
                                        yield delta["text"]
                            except json.JSONDecodeError:
                                continue

            self._record_success()

        except Exception as e:
            self._record_failure()
            logger.error(f"Claude streaming request failed: {e}")
            raise

    def _prepare_payload(self, request: ModelRequest) -> dict[str, Any]:
        """Prepare API request payload."""
        messages = []

        # Add system message if provided
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        # Add user message
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self.model_name,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "messages": messages,
        }

        # Add stop sequences if provided
        if request.stop_sequences:
            payload["stop_sequences"] = request.stop_sequences

        return payload

    def _parse_response(
        self, result: dict[str, Any], start_time: float
    ) -> ModelResponse:
        """Parse API response."""
        content = ""

        # Extract content from response
        if result.get("content"):
            for content_block in result["content"]:
                if content_block.get("type") == "text":
                    content += content_block.get("text", "")

        # Extract usage information
        usage = result.get("usage", {})

        return ModelResponse(
            content=content,
            model=result.get("model", self.model_name),
            usage={
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0)
                + usage.get("output_tokens", 0),
            },
            finish_reason=result.get("stop_reason", "unknown"),
            response_time=time.time() - start_time,
            metadata={
                "anthropic_id": result.get("id"),
                "anthropic_type": result.get("type"),
                "anthropic_role": result.get("role"),
            },
        )

    async def _handle_error_response(self, response: httpx.Response):
        """Handle API error responses."""
        try:
            error_data = response.json()
            error_type = error_data.get("error", {}).get("type", "unknown")
            error_message = error_data.get("error", {}).get("message", "Unknown error")
        except:
            error_type = "unknown"
            error_message = f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed: {error_message}")
        if response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded: {error_message}")
        if response.status_code == 400 and "token" in error_message.lower():
            raise TokenLimitError(f"Token limit exceeded: {error_message}")
        if response.status_code >= 500:
            raise ModelUnavailableError(f"Claude service unavailable: {error_message}")
        raise ModelClientError(f"Claude API error ({error_type}): {error_message}")

    def _update_usage(self, usage: dict[str, int]):
        """Update usage statistics."""
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        self.total_tokens += prompt_tokens + completion_tokens

        # Calculate cost
        input_cost = (prompt_tokens / 1000) * self.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * self.output_cost_per_1k
        self.total_cost += input_cost + output_cost

    def _calculate_cost(self, usage: dict[str, int]) -> float:
        """Calculate cost for this request."""
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * self.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * self.output_cost_per_1k

        return input_cost + output_cost
