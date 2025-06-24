"""
Model router for intelligent model selection and load balancing.
"""

import asyncio
import logging
import random
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from ..config import settings
from .claude_client import ClaudeClient
from .model_client import ModelClient, ModelRequest, ModelResponse
from .openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Available model providers."""

    CLAUDE = "claude"
    OPENAI = "openai"


class ModelRouter:
    """
    Intelligent model router for selecting optimal models.

    Provides load balancing, failover, and cost optimization
    across multiple foundation model providers.
    """

    def __init__(self):
        self.clients: Dict[str, ModelClient] = {}
        self.provider_configs = {
            ModelProvider.CLAUDE: {
                "client_class": ClaudeClient,
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
                "max_tokens": 4096,
                "strengths": ["reasoning", "analysis", "safety"],
                "api_key_env": "ANTHROPIC_API_KEY",
            },
            ModelProvider.OPENAI: {
                "client_class": OpenAIClient,
                "models": ["gpt-4o", "gpt-4o-mini"],
                "cost_per_1k_input": 0.005,
                "cost_per_1k_output": 0.015,
                "max_tokens": 4096,
                "strengths": ["coding", "structured_output", "function_calling"],
                "api_key_env": "OPENAI_API_KEY",
            },
        }

        # Routing strategies
        self.routing_strategies = {
            "cost_optimized": self._route_cost_optimized,
            "performance_optimized": self._route_performance_optimized,
            "load_balanced": self._route_load_balanced,
            "failover": self._route_failover,
        }

        # Model performance tracking
        self.model_stats: Dict[str, Dict[str, Any]] = {}

        # Initialize clients
        asyncio.create_task(self._initialize_clients())

    async def _initialize_clients(self):
        """Initialize model clients."""
        try:
            for provider, config in self.provider_configs.items():
                api_key = getattr(settings, config["api_key_env"], None)

                if not api_key:
                    logger.warning(f"No API key found for {provider.value}")
                    continue

                for model_name in config["models"]:
                    client_id = f"{provider.value}:{model_name}"

                    try:
                        client = config["client_class"](
                            api_key=api_key,
                            model_name=model_name,
                            timeout=settings.MODEL_TIMEOUT,
                            max_retries=settings.MODEL_MAX_RETRIES,
                        )

                        self.clients[client_id] = client
                        self.model_stats[client_id] = {
                            "requests": 0,
                            "successes": 0,
                            "failures": 0,
                            "avg_response_time": 0.0,
                            "total_cost": 0.0,
                            "last_used": None,
                        }

                        logger.info(f"Initialized client for {client_id}")

                    except Exception as e:
                        logger.error(f"Failed to initialize client for {client_id}: {e}")

            logger.info(f"Initialized {len(self.clients)} model clients")

        except Exception as e:
            logger.error(f"Failed to initialize model clients: {e}")

    async def generate(
        self,
        request: ModelRequest,
        strategy: str = "performance_optimized",
        preferred_provider: Optional[ModelProvider] = None,
        task_type: Optional[str] = None,
    ) -> ModelResponse:
        """
        Generate response using optimal model selection.

        Args:
            request: Model request
            strategy: Routing strategy
            preferred_provider: Preferred model provider
            task_type: Type of task (reasoning, coding, analysis, etc.)

        Returns:
            Model response
        """
        try:
            # Select optimal model
            selected_client_id = await self._select_model(
                request, strategy, preferred_provider, task_type
            )

            if not selected_client_id:
                raise Exception("No available models")

            client = self.clients[selected_client_id]

            # Update request stats
            self.model_stats[selected_client_id]["requests"] += 1

            try:
                # Generate response
                response = await client.generate(request)

                # Update success stats
                self._update_success_stats(selected_client_id, response)

                return response

            except Exception as e:
                # Update failure stats
                self._update_failure_stats(selected_client_id)

                # Try fallback if available
                fallback_client_id = await self._get_fallback_model(selected_client_id)
                if fallback_client_id:
                    logger.warning(
                        f"Falling back to {fallback_client_id} after {selected_client_id} failed"
                    )
                    fallback_client = self.clients[fallback_client_id]
                    response = await fallback_client.generate(request)
                    self._update_success_stats(fallback_client_id, response)
                    return response

                raise e

        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            raise

    async def generate_stream(
        self,
        request: ModelRequest,
        strategy: str = "performance_optimized",
        preferred_provider: Optional[ModelProvider] = None,
        task_type: Optional[str] = None,
    ):
        """Generate streaming response using optimal model selection."""
        try:
            # Select optimal model
            selected_client_id = await self._select_model(
                request, strategy, preferred_provider, task_type
            )

            if not selected_client_id:
                raise Exception("No available models")

            client = self.clients[selected_client_id]

            # Update request stats
            self.model_stats[selected_client_id]["requests"] += 1

            try:
                # Generate streaming response
                async for chunk in client.generate_stream(request):
                    yield chunk

                # Update success stats (simplified for streaming)
                self.model_stats[selected_client_id]["successes"] += 1

            except Exception as e:
                # Update failure stats
                self._update_failure_stats(selected_client_id)
                raise e

        except Exception as e:
            logger.error(f"Model streaming generation failed: {e}")
            raise

    async def _select_model(
        self,
        request: ModelRequest,
        strategy: str,
        preferred_provider: Optional[ModelProvider],
        task_type: Optional[str],
    ) -> Optional[str]:
        """Select optimal model based on strategy and requirements."""
        if not self.clients:
            return None

        # Filter by preferred provider if specified
        available_clients = self.clients.keys()
        if preferred_provider:
            available_clients = [
                client_id
                for client_id in available_clients
                if client_id.startswith(preferred_provider.value)
            ]

        # Filter by task type strengths
        if task_type:
            suitable_clients = []
            for client_id in available_clients:
                provider_name = client_id.split(":")[0]
                provider = ModelProvider(provider_name)
                strengths = self.provider_configs[provider]["strengths"]

                if task_type in strengths:
                    suitable_clients.append(client_id)

            if suitable_clients:
                available_clients = suitable_clients

        # Apply routing strategy
        if strategy in self.routing_strategies:
            return await self.routing_strategies[strategy](list(available_clients))
        else:
            # Default to random selection
            return random.choice(list(available_clients))

    async def _route_cost_optimized(self, available_clients: List[str]) -> str:
        """Route to most cost-effective model."""
        if not available_clients:
            return None

        # Calculate cost per client
        costs = {}
        for client_id in available_clients:
            provider_name = client_id.split(":")[0]
            provider = ModelProvider(provider_name)
            config = self.provider_configs[provider]

            # Simple cost calculation (could be more sophisticated)
            avg_cost = (config["cost_per_1k_input"] + config["cost_per_1k_output"]) / 2
            costs[client_id] = avg_cost

        # Return cheapest option
        return min(costs.keys(), key=lambda x: costs[x])

    async def _route_performance_optimized(self, available_clients: List[str]) -> str:
        """Route to best performing model."""
        if not available_clients:
            return None

        # Calculate performance scores
        scores = {}
        for client_id in available_clients:
            stats = self.model_stats[client_id]

            if stats["requests"] == 0:
                # New model, give it a chance
                scores[client_id] = 1.0
            else:
                success_rate = stats["successes"] / stats["requests"]
                # Inverse of response time (faster = better)
                speed_score = 1.0 / max(stats["avg_response_time"], 0.1)

                # Combined score
                scores[client_id] = success_rate * speed_score

        # Return best performing option
        return max(scores.keys(), key=lambda x: scores[x])

    async def _route_load_balanced(self, available_clients: List[str]) -> str:
        """Route using load balancing."""
        if not available_clients:
            return None

        # Simple round-robin based on request count
        request_counts = {
            client_id: self.model_stats[client_id]["requests"] for client_id in available_clients
        }

        # Return client with least requests
        return min(request_counts.keys(), key=lambda x: request_counts[x])

    async def _route_failover(self, available_clients: List[str]) -> str:
        """Route with failover priority."""
        if not available_clients:
            return None

        # Prefer clients with recent success
        for client_id in available_clients:
            stats = self.model_stats[client_id]
            if stats["requests"] == 0 or stats["successes"] / stats["requests"] > 0.8:
                return client_id

        # Fallback to any available client
        return available_clients[0]

    async def _get_fallback_model(self, failed_client_id: str) -> Optional[str]:
        """Get fallback model for failed client."""
        # Get different provider
        failed_provider = failed_client_id.split(":")[0]

        for client_id in self.clients.keys():
            if not client_id.startswith(failed_provider):
                return client_id

        return None

    def _update_success_stats(self, client_id: str, response: ModelResponse):
        """Update success statistics."""
        stats = self.model_stats[client_id]
        stats["successes"] += 1

        # Update average response time
        if stats["successes"] == 1:
            stats["avg_response_time"] = response.response_time
        else:
            stats["avg_response_time"] = (
                stats["avg_response_time"] * (stats["successes"] - 1) + response.response_time
            ) / stats["successes"]

        stats["last_used"] = asyncio.get_event_loop().time()

    def _update_failure_stats(self, client_id: str):
        """Update failure statistics."""
        self.model_stats[client_id]["failures"] += 1

    def get_router_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            "available_clients": list(self.clients.keys()),
            "model_stats": self.model_stats,
            "total_requests": sum(stats["requests"] for stats in self.model_stats.values()),
            "total_successes": sum(stats["successes"] for stats in self.model_stats.values()),
            "total_failures": sum(stats["failures"] for stats in self.model_stats.values()),
        }
