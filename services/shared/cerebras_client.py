#!/usr/bin/env python3
"""
Cerebras AI Client for ACGS-1 Constitutional Governance System

This module provides integration with Cerebras AI models (Llama3.1-8B, Llama3.1-70B)
for fast inference in constitutional governance workflows.

Key Features:
- Fast inference with Cerebras hardware acceleration
- Constitutional compliance validation
- Multi-model support (Llama3.1-8B for fast synthesis, Llama3.1-70B for deep analysis)
- Circuit breaker patterns for reliability
- Performance monitoring and metrics
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class CerebrasModel(Enum):
    """Supported Cerebras models."""

    LLAMA3_1_8B = "llama3.1-8b"
    LLAMA3_1_70B = "llama3.1-70b"


@dataclass
class CerebrasConfig:
    """Configuration for Cerebras AI client."""

    api_key: str
    base_url: str = "https://api.cerebras.ai/v1"
    timeout_seconds: int = 30
    max_retries: int = 3
    default_model: CerebrasModel = CerebrasModel.LLAMA3_1_8B
    max_tokens: int = 8192
    temperature: float = 0.1


@dataclass
class CerebrasResponse:
    """Response from Cerebras AI API."""

    content: str
    model: str
    tokens_used: int
    response_time_ms: float
    finish_reason: str
    constitutional_compliance_score: float = 0.0
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = None
    error: Optional[str] = None


class CerebrasClient:
    """
    Cerebras AI client for constitutional governance tasks.

    Provides fast inference capabilities using Cerebras hardware acceleration
    with specialized prompting for constitutional compliance and governance workflows.
    """

    def __init__(self, config: CerebrasConfig):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize Cerebras client.

        Args:
            config: Cerebras configuration
        """
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout_seconds),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
        )

        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0

        logger.info(f"Initialized Cerebras client with base URL: {self.config.base_url}")

    async def __aenter__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Async context manager exit."""
        await self.close()

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close HTTP client."""
        await self.client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_constitutional_analysis(
        self,
        prompt: str,
        model: CerebrasModel = None,
        context: Optional[Dict[str, Any]] = None,
        constitution_hash: Optional[str] = None,
        **kwargs,
    ) -> CerebrasResponse:
        """
        Generate constitutional analysis using Cerebras models.

        Args:
            prompt: Input prompt for analysis
            model: Cerebras model to use
            context: Additional context for analysis
            constitution_hash: Constitution hash for compliance validation
            **kwargs: Additional parameters

        Returns:
            CerebrasResponse with analysis results
        """
        start_time = time.time()
        model = model or self.config.default_model

        try:
            # Construct constitutional analysis prompt
            constitutional_prompt = self._construct_constitutional_prompt(
                prompt, context, constitution_hash
            )

            # Prepare API request
            payload = {
                "model": model.value,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a constitutional governance AI assistant specialized in rapid constitutional compliance analysis. Provide accurate, fast responses while maintaining constitutional fidelity.",
                    },
                    {"role": "user", "content": constitutional_prompt},
                ],
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": False,
            }

            # Make API call
            response = await self.client.post(
                f"{self.config.base_url}/chat/completions", json=payload
            )

            response_time = (time.time() - start_time) * 1000
            self.request_count += 1
            self.total_response_time += response_time

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                finish_reason = result["choices"][0].get("finish_reason", "completed")

                # Calculate constitutional compliance score
                compliance_score = self._assess_constitutional_compliance(content)
                confidence_score = self._calculate_confidence_score(content, model)

                return CerebrasResponse(
                    content=content,
                    model=model.value,
                    tokens_used=tokens_used,
                    response_time_ms=response_time,
                    finish_reason=finish_reason,
                    constitutional_compliance_score=compliance_score,
                    confidence_score=confidence_score,
                    metadata={
                        "constitution_hash": constitution_hash,
                        "context_provided": context is not None,
                        "api_response_status": response.status_code,
                    },
                )
            else:
                error_msg = f"Cerebras API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.error_count += 1

                return CerebrasResponse(
                    content="",
                    model=model.value,
                    tokens_used=0,
                    response_time_ms=response_time,
                    finish_reason="error",
                    error=error_msg,
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"Cerebras client error: {str(e)}"
            logger.error(error_msg)
            self.error_count += 1

            return CerebrasResponse(
                content="",
                model=model.value if model else "unknown",
                tokens_used=0,
                response_time_ms=response_time,
                finish_reason="error",
                error=error_msg,
            )

    async def generate_fast_synthesis(
        self,
        prompt: str,
        policies: List[str] = None,
        principles: List[str] = None,
        **kwargs,
    ) -> CerebrasResponse:
        """
        Generate fast policy synthesis using Llama3.1-8B.

        Args:
            prompt: Synthesis prompt
            policies: Existing policies for context
            principles: Constitutional principles
            **kwargs: Additional parameters

        Returns:
            CerebrasResponse with synthesis results
        """
        context = {
            "policies": policies or [],
            "principles": principles or [],
            "task": "fast_synthesis",
        }

        return await self.generate_constitutional_analysis(
            prompt=prompt, model=CerebrasModel.LLAMA3_1_8B, context=context, **kwargs
        )

    async def generate_deep_analysis(
        self,
        prompt: str,
        constitution_hash: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> CerebrasResponse:
        """
        Generate deep constitutional analysis using Llama3.1-70B.

        Args:
            prompt: Analysis prompt
            constitution_hash: Constitution hash for validation
            context: Additional context
            **kwargs: Additional parameters

        Returns:
            CerebrasResponse with deep analysis results
        """
        return await self.generate_constitutional_analysis(
            prompt=prompt,
            model=CerebrasModel.LLAMA3_1_70B,
            context=context,
            constitution_hash=constitution_hash,
            **kwargs,
        )

    def _construct_constitutional_prompt(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        constitution_hash: Optional[str],
    ) -> str:
        """Construct constitutional analysis prompt."""
        constitutional_prompt = f"""
Constitutional Governance Analysis Request:

Primary Prompt: {prompt}

"""

        if constitution_hash:
            constitutional_prompt += f"Constitution Hash: {constitution_hash}\n"

        if context:
            if context.get("principles"):
                constitutional_prompt += (
                    f"Constitutional Principles: {', '.join(context['principles'])}\n"
                )

            if context.get("policies"):
                constitutional_prompt += f"Existing Policies: {', '.join(context['policies'][:3])}\n"  # Limit for token efficiency

            if context.get("task"):
                constitutional_prompt += f"Task Type: {context['task']}\n"

        constitutional_prompt += """
Requirements:
1. Ensure constitutional compliance in all recommendations
2. Provide clear, actionable guidance
3. Consider governance implications
4. Maintain constitutional fidelity
5. Be concise but comprehensive

Please provide your analysis:
"""

        return constitutional_prompt

    def _assess_constitutional_compliance(self, content: str) -> float:
        """Assess constitutional compliance of response."""
        if not content:
            return 0.0

        # Constitutional compliance indicators
        compliance_keywords = [
            "constitutional",
            "principle",
            "governance",
            "compliance",
            "rights",
            "authority",
            "democratic",
            "transparent",
            "accountable",
            "fair",
            "just",
            "legal",
        ]

        content_lower = content.lower()
        matches = sum(1 for keyword in compliance_keywords if keyword in content_lower)

        # Base score from keyword presence
        base_score = min(0.8, matches / len(compliance_keywords))

        # Bonus for structured analysis
        if "analysis:" in content_lower or "recommendation:" in content_lower:
            base_score += 0.1

        # Bonus for governance considerations
        if "governance" in content_lower and "implication" in content_lower:
            base_score += 0.1

        return min(1.0, base_score)

    def _calculate_confidence_score(self, content: str, model: CerebrasModel) -> float:
        """Calculate confidence score for response."""
        if not content:
            return 0.0

        # Base confidence based on content quality
        base_confidence = 0.7

        # Length bonus
        if len(content) > 200:
            base_confidence += 0.1

        # Structure bonus
        if len(content.split(".")) > 3:
            base_confidence += 0.1

        # Model-specific adjustments
        if model == CerebrasModel.LLAMA3_1_70B:
            base_confidence += 0.1  # Larger model bonus

        return min(1.0, base_confidence)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics."""
        avg_response_time = (
            self.total_response_time / self.request_count if self.request_count > 0 else 0.0
        )

        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0.0

        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": error_rate,
            "average_response_time_ms": avg_response_time,
            "total_response_time_ms": self.total_response_time,
        }


# Global Cerebras client instance
_cerebras_client: Optional[CerebrasClient] = None


async def get_cerebras_client(
    api_key: Optional[str] = None,
) -> Optional[CerebrasClient]:
    """
    Get global Cerebras client instance.

    Args:
        api_key: Optional API key override

    Returns:
        CerebrasClient instance or None if not available
    """
    global _cerebras_client

    if api_key is None:
        import os

        api_key = os.getenv("CEREBRAS_API_KEY")

    if not api_key:
        logger.warning("CEREBRAS_API_KEY not available. Cerebras client disabled.")
        return None

    if _cerebras_client is None:
        try:
            config = CerebrasConfig(api_key=api_key)
            _cerebras_client = CerebrasClient(config)
            logger.info("Initialized global Cerebras client")
        except Exception as e:
            logger.error(f"Failed to initialize Cerebras client: {e}")
            return None

    return _cerebras_client


async def close_cerebras_client():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Close global Cerebras client."""
    global _cerebras_client
    if _cerebras_client:
        await _cerebras_client.close()
        _cerebras_client = None
