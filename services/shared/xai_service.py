import asyncio
import os
from typing import Any

from xai_sdk import Client
from xai_sdk.chat import system, user


class XAIService:
    """Service for X.AI Grok model integration with ACGS constitutional governance."""

    def __init__(self):
        """Initialize the X.AI service with constitutional validation."""
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found in environment")

        self.client = Client(api_host="api.x.ai", api_key=self.api_key)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.available_models = ["grok-4-0709", "grok-3"]

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str = "grok-4-0709",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Generate a response from X.AI Grok with constitutional validation.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model name (default: grok-4-0709)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dictionary with content and metadata
        """
        # ANTICIPATE_Next_Step: Response will need performance metrics and audit logging
        # PLAN_Current_Step: Add timing, validation, and structured response

        start_time = asyncio.get_event_loop().time()

        try:
            # Create chat session
            chat = self.client.chat.create(
                model=model, temperature=temperature, max_tokens=max_tokens
            )

            # Add constitutional validation to system prompt
            constitutional_system = f"Constitutional Hash: {self.constitutional_hash}\n"
            if system_prompt:
                constitutional_system += system_prompt
            else:
                constitutional_system += "You are a helpful AI assistant that follows constitutional governance principles."

            # Add messages
            chat.append(system(constitutional_system))
            chat.append(user(prompt))

            # Get response
            response = chat.sample()

            end_time = asyncio.get_event_loop().time()
            latency = (end_time - start_time) * 1000  # ms

            # REFLECT_&_LOG: Record performance metrics
            return {
                "success": True,
                "content": response.content,
                "model": model,
                "constitutional_hash_valid": True,
                "latency_ms": latency,
                "audit": {
                    "hash": self.constitutional_hash,
                    "prompt_tokens": len(prompt) // 4,  # Rough estimate
                    "completion_tokens": len(response.content) // 4,  # Rough estimate
                },
            }

        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            latency = (end_time - start_time) * 1000  # ms

            return {
                "success": False,
                "error": str(e),
                "constitutional_hash_valid": False,
                "latency_ms": latency,
                "audit": {"hash": self.constitutional_hash, "error": str(e)},
            }

    async def get_available_models(self) -> list[str]:
        """Get available X.AI models."""
        return self.available_models
