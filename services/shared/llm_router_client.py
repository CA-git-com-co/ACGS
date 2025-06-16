"""
NVIDIA LLM Router Client Library

Async-compatible client for integrating with the NVIDIA LLM Router service.
Provides high-level interfaces for task-based and complexity-based routing.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import aiohttp
import backoff

from services.shared.auth import get_auth_headers
from services.shared.utils import get_logger


class TaskType(Enum):
    """Supported task types for routing"""

    CONSTITUTIONAL_ANALYSIS = "constitutional_analysis"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    POLICY_SYNTHESIS = "policy_synthesis"
    POLICY_REVIEW = "policy_review"
    COMPLIANCE_ENFORCEMENT = "compliance_enforcement"
    VIOLATION_DETECTION = "violation_detection"
    CONTENT_GENERATION = "content_generation"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"


class ComplexityLevel(Enum):
    """Request complexity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ChatMessage:
    """Chat message structure"""

    role: str  # "user", "assistant", "system"
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RouterRequest:
    """LLM Router request structure"""

    messages: List[ChatMessage]
    task_type: Optional[TaskType] = None
    complexity: Optional[ComplexityLevel] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RouterResponse:
    """LLM Router response structure"""

    content: str
    model_used: str
    task_type: Optional[str] = None
    complexity_detected: Optional[str] = None
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMRouterError(Exception):
    """Base exception for LLM Router errors"""

    pass


class LLMRouterTimeoutError(LLMRouterError):
    """Timeout error"""

    pass


class LLMRouterAuthError(LLMRouterError):
    """Authentication error"""

    pass


class LLMRouterClient:
    """
    Async client for NVIDIA LLM Router service

    Features:
    - Task-based and complexity-based routing
    - Session management with connection pooling
    - Automatic retries with exponential backoff
    - Streaming support for long responses
    - Constitutional governance integration
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        auth_token: Optional[str] = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.logger = get_logger(__name__)

        # Configuration
        self.base_url = base_url or "http://nvidia_llm_router_server:8081"
        self.timeout = timeout
        self.max_retries = max_retries
        self.auth_token = auth_token

        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_timeout = aiohttp.ClientTimeout(total=timeout)

        # Request tracking
        self._request_count = 0
        self._error_count = 0

        self.logger.info(f"LLMRouterClient initialized with base_url: {self.base_url}")

    async def __aenter__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Ensure aiohttp session is created"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100, limit_per_host=20, keepalive_timeout=30, enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=self._session_timeout,
                headers={"Content-Type": "application/json"},
            )

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @backoff.on_exception(
        backoff.expo, (aiohttp.ClientError, asyncio.TimeoutError), max_tries=3, max_time=60
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        await self._ensure_session()

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Prepare headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        # Add authentication if available
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        else:
            # Try to get auth headers from shared auth module
            try:
                auth_headers = await get_auth_headers()
                request_headers.update(auth_headers)
            except Exception as e:
                self.logger.debug(f"Could not get auth headers: {e}")

        # Add request tracking
        request_headers["X-Request-ID"] = f"llm-router-{self._request_count}"
        self._request_count += 1

        try:
            async with self._session.request(
                method=method, url=url, json=data, headers=request_headers
            ) as response:

                if response.status == 401:
                    raise LLMRouterAuthError("Authentication failed")
                elif response.status == 408:
                    raise LLMRouterTimeoutError("Request timeout")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise LLMRouterError(f"HTTP {response.status}: {error_text}")

                return await response.json()

        except asyncio.TimeoutError:
            self._error_count += 1
            raise LLMRouterTimeoutError("Request timeout")
        except aiohttp.ClientError as e:
            self._error_count += 1
            raise LLMRouterError(f"Client error: {str(e)}")

    async def chat_completion(
        self,
        messages: List[Union[ChatMessage, Dict[str, str]]],
        task_type: Optional[TaskType] = None,
        complexity: Optional[ComplexityLevel] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RouterResponse:
        """
        Send chat completion request to LLM Router

        Args:
            messages: List of chat messages
            task_type: Task type for routing optimization
            complexity: Complexity level for model selection
            model: Specific model to use (overrides routing)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Enable streaming response
            metadata: Additional metadata for routing

        Returns:
            RouterResponse with generated content and metadata
        """
        # Convert messages to ChatMessage objects if needed
        chat_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                chat_messages.append(
                    ChatMessage(
                        role=msg["role"], content=msg["content"], metadata=msg.get("metadata")
                    )
                )
            else:
                chat_messages.append(msg)

        # Prepare request
        request_data = {"messages": [asdict(msg) for msg in chat_messages], "stream": stream}

        # Add optional parameters
        if task_type:
            request_data["task_type"] = task_type.value
        if complexity:
            request_data["complexity"] = complexity.value
        if model:
            request_data["model"] = model
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        if temperature is not None:
            request_data["temperature"] = temperature
        if metadata:
            request_data["metadata"] = metadata

        # Add ACGS-specific metadata
        request_data["acgs_metadata"] = {
            "client": "llm_router_client",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": f"acgs-{self._request_count}",
        }

        try:
            if stream:
                return await self._stream_completion(request_data)
            else:
                response_data = await self._make_request(
                    method="POST", endpoint="/v1/chat/completions", data=request_data
                )
                return self._parse_response(response_data)

        except Exception as e:
            self.logger.error(f"Chat completion failed: {str(e)}")
            raise

    async def constitutional_request(
        self,
        content: str,
        analysis_type: str = "compliance_check",
        constitutional_principles: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RouterResponse:
        """
        Send constitutional analysis request with optimized routing

        Args:
            content: Content to analyze
            analysis_type: Type of constitutional analysis
            constitutional_principles: Specific principles to check
            metadata: Additional metadata

        Returns:
            RouterResponse with constitutional analysis
        """
        messages = [
            ChatMessage(
                role="system",
                content="You are a constitutional AI assistant specialized in governance analysis.",
            ),
            ChatMessage(
                role="user",
                content=content,
                metadata={
                    "analysis_type": analysis_type,
                    "constitutional_principles": constitutional_principles or [],
                },
            ),
        ]

        # Use constitutional analysis task type and high complexity
        return await self.chat_completion(
            messages=messages,
            task_type=TaskType.CONSTITUTIONAL_ANALYSIS,
            complexity=ComplexityLevel.HIGH,
            temperature=0.1,  # Low temperature for consistency
            metadata={
                "constitutional_analysis": True,
                "analysis_type": analysis_type,
                "principles": constitutional_principles,
                **(metadata or {}),
            },
        )

    async def policy_synthesis_request(
        self,
        requirements: str,
        context: Optional[str] = None,
        stakeholders: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RouterResponse:
        """
        Send policy synthesis request with optimized routing

        Args:
            requirements: Policy requirements
            context: Additional context
            stakeholders: Relevant stakeholders
            metadata: Additional metadata

        Returns:
            RouterResponse with synthesized policy
        """
        system_message = (
            "You are a policy synthesis AI specialized in creating governance policies."
        )

        user_content = f"Requirements: {requirements}"
        if context:
            user_content += f"\n\nContext: {context}"
        if stakeholders:
            user_content += f"\n\nStakeholders: {', '.join(stakeholders)}"

        messages = [
            ChatMessage(role="system", content=system_message),
            ChatMessage(
                role="user",
                content=user_content,
                metadata={"stakeholders": stakeholders or [], "synthesis_type": "policy_creation"},
            ),
        ]

        return await self.chat_completion(
            messages=messages,
            task_type=TaskType.POLICY_SYNTHESIS,
            complexity=ComplexityLevel.HIGH,
            temperature=0.2,
            metadata={"policy_synthesis": True, "stakeholders": stakeholders, **(metadata or {})},
        )

    async def _stream_completion(self, request_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Handle streaming completion (placeholder for future implementation)"""
        # For now, fall back to non-streaming
        request_data["stream"] = False
        response_data = await self._make_request(
            method="POST", endpoint="/v1/chat/completions", data=request_data
        )
        response = self._parse_response(response_data)
        yield response.content

    def _parse_response(self, response_data: Dict[str, Any]) -> RouterResponse:
        """Parse API response into RouterResponse object"""
        # Handle OpenAI-compatible response format
        if "choices" in response_data:
            choice = response_data["choices"][0]
            content = choice["message"]["content"]
        else:
            content = response_data.get("content", "")

        return RouterResponse(
            content=content,
            model_used=response_data.get("model", "unknown"),
            task_type=response_data.get("task_type"),
            complexity_detected=response_data.get("complexity_detected"),
            latency_ms=response_data.get("latency_ms"),
            tokens_used=response_data.get("usage", {}).get("total_tokens"),
            confidence_score=response_data.get("confidence_score"),
            metadata=response_data.get("metadata", {}),
        )

    async def health_check(self) -> Dict[str, Any]:
        """Check router service health"""
        return await self._make_request("GET", "/health")

    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models"""
        return await self._make_request("GET", "/v1/models")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get router metrics"""
        return await self._make_request("GET", "/metrics")


# Convenience functions for common use cases
async def quick_constitutional_analysis(content: str) -> str:
    """Quick constitutional analysis with default settings"""
    async with LLMRouterClient() as client:
        response = await client.constitutional_request(content)
        return response.content


async def quick_policy_synthesis(requirements: str) -> str:
    """Quick policy synthesis with default settings"""
    async with LLMRouterClient() as client:
        response = await client.policy_synthesis_request(requirements)
        return response.content


async def quick_chat(message: str, task_type: Optional[TaskType] = None) -> str:
    """Quick chat completion with default settings"""
    async with LLMRouterClient() as client:
        messages = [ChatMessage(role="user", content=message)]
        response = await client.chat_completion(messages, task_type=task_type)
        return response.content
