"""
AI Model Service for ACGS.

This module provides a unified interface for AI model interactions
across different providers and model types in the ACGS system.
"""

import asyncio
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class ModelProvider(str, Enum):
    """Supported AI model providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    LOCAL = "local"


class ModelType(str, Enum):
    """Types of AI models"""

    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    ANALYSIS = "analysis"


class ModelRequest(BaseModel):
    """Request to an AI model"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    model_type: ModelType
    provider: ModelProvider
    model_name: str
    prompt: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelResponse(BaseModel):
    """Response from an AI model"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    request_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] | None = None
    confidence_score: float | None = None
    processing_time_ms: int | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIModelService:
    """
    AI Model Service for ACGS multi-agent operations.

    Provides a unified interface for interacting with various AI models
    across different providers, with support for:
    - Multiple model providers (OpenAI, Anthropic, Groq, Local)
    - Different model types (chat, completion, embedding, etc.)
    - Request/response tracking
    - Error handling and retries
    - Performance monitoring
    """

    def __init__(self, default_provider: ModelProvider = ModelProvider.OPENAI):
        self.logger = logging.getLogger(__name__)
        self.default_provider = default_provider
        self.request_history: list[ModelRequest] = []
        self.response_history: list[ModelResponse] = []
        self.max_history = 1000

        # Model configurations
        self.model_configs = {
            ModelProvider.OPENAI: {
                "chat": ["gpt-4", "gpt-3.5-turbo"],
                "completion": ["text-davinci-003"],
                "embedding": ["text-embedding-ada-002"],
            },
            ModelProvider.ANTHROPIC: {
                "chat": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "completion": ["claude-instant-1"],
            },
            ModelProvider.GROQ: {
                "chat": ["llama2-70b-4096", "mixtral-8x7b-32768"],
                "completion": ["llama2-70b-4096"],
            },
            ModelProvider.OPENROUTER: {
                "chat": ["openrouter/cypher-alpha:free"],
                "completion": ["openrouter/cypher-alpha:free"],
                "analysis": ["openrouter/cypher-alpha:free"],
                "constitutional_validation": ["openrouter/cypher-alpha:free"],
            },
            ModelProvider.LOCAL: {
                "chat": ["local-llm"],
                "completion": ["local-llm"],
                "classification": ["local-classifier"],
            },
        }

        # OpenRouter client initialization
        self.openrouter_client = None
        self._initialize_openrouter_client()

    def _initialize_openrouter_client(self) -> None:
        """Initialize OpenRouter client if API key is available"""
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key and OpenAI:
                self.openrouter_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1", api_key=api_key
                )
                self.logger.info("OpenRouter client initialized successfully")
            else:
                self.logger.warning(
                    "OpenRouter API key not found or OpenAI library not available"
                )
        except Exception as e:
            self.logger.exception(f"Failed to initialize OpenRouter client: {e}")

    async def generate_response(self, request: ModelRequest) -> ModelResponse:
        """Generate a response using the specified AI model"""
        start_time = datetime.utcnow()

        try:
            # Add to request history
            self.request_history.append(request)
            if len(self.request_history) > self.max_history:
                self.request_history.pop(0)

            # Validate model availability
            if not self._is_model_available(
                request.provider, request.model_type, request.model_name
            ):
                raise ValueError(
                    f"Model {request.model_name} not available for {request.provider}/{request.model_type}"
                )

            # Generate response based on provider
            content = await self._generate_content(request)

            # Calculate processing time
            processing_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            # Create response
            response = ModelResponse(
                request_id=request.id,
                content=content,
                metadata={
                    "provider": request.provider,
                    "model_name": request.model_name,
                    "model_type": request.model_type,
                },
                processing_time_ms=processing_time,
                confidence_score=0.85,  # Placeholder confidence score
            )

            # Add to response history
            self.response_history.append(response)
            if len(self.response_history) > self.max_history:
                self.response_history.pop(0)

            self.logger.info(
                f"Generated response for {request.model_name} in {processing_time}ms"
            )
            return response

        except Exception as e:
            self.logger.exception(f"Error generating response: {e}")
            # Return error response
            return ModelResponse(
                request_id=request.id,
                content=f"Error: {e!s}",
                metadata={"error": True, "error_message": str(e)},
                confidence_score=0.0,
            )

    async def _generate_content(self, request: ModelRequest) -> str:
        """Generate content based on the model provider and type"""
        # This is a simplified implementation - in practice, this would
        # interface with actual AI model APIs

        if request.provider == ModelProvider.OPENAI:
            return await self._generate_openai_content(request)
        if request.provider == ModelProvider.ANTHROPIC:
            return await self._generate_anthropic_content(request)
        if request.provider == ModelProvider.GROQ:
            return await self._generate_groq_content(request)
        if request.provider == ModelProvider.OPENROUTER:
            return await self._generate_openrouter_content(request)
        if request.provider == ModelProvider.LOCAL:
            return await self._generate_local_content(request)
        raise ValueError(f"Unsupported provider: {request.provider}")

    async def _generate_openai_content(self, request: ModelRequest) -> str:
        """Generate content using OpenAI models"""
        # Simulate API call delay
        await asyncio.sleep(0.1)

        if request.model_type == ModelType.CHAT:
            return f"OpenAI {request.model_name} response to: {request.prompt[:50]}..."
        if request.model_type == ModelType.COMPLETION:
            return f"OpenAI completion: {request.prompt[:30]}... [completed]"
        if request.model_type == ModelType.EMBEDDING:
            return "[0.1, 0.2, 0.3, ...]"  # Placeholder embedding
        return f"OpenAI {request.model_type} response"

    async def _generate_anthropic_content(self, request: ModelRequest) -> str:
        """Generate content using Anthropic models"""
        await asyncio.sleep(0.1)

        if request.model_type == ModelType.CHAT:
            return f"Claude {request.model_name} response to: {request.prompt[:50]}..."
        return f"Anthropic {request.model_type} response"

    async def _generate_groq_content(self, request: ModelRequest) -> str:
        """Generate content using Groq models"""
        await asyncio.sleep(0.05)  # Groq is faster

        return f"Groq {request.model_name} response to: {request.prompt[:50]}..."

    async def _generate_openrouter_content(self, request: ModelRequest) -> str:
        """Generate content using OpenRouter models"""
        if not self.openrouter_client:
            raise ValueError("OpenRouter client not initialized. Check API key.")

        try:
            # Prepare messages for chat completion
            messages = [{"role": "user", "content": request.prompt}]

            # Add system message for constitutional validation tasks
            if (
                request.model_type == ModelType.ANALYSIS
                and "constitutional" in request.prompt.lower()
            ):
                system_prompt = """You are a constitutional AI validator for the ACGS system.
                Analyze the provided content for compliance with constitutional principles:
                - Human oversight requirements
                - Data privacy protection
                - Transparent decision making
                - Resource usage limits
                - Security compliance

                Provide a structured analysis with compliance status, violations, and recommendations."""
                messages.insert(0, {"role": "system", "content": system_prompt})

            # Make the API call
            completion = self.openrouter_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://acgs.ai",
                    "X-Title": "ACGS Constitutional AI System",
                },
                model=request.model_name,
                messages=messages,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7,
            )

            return completion.choices[0].message.content

        except Exception as e:
            self.logger.exception(f"OpenRouter API error: {e}")
            return f"OpenRouter error: {e!s}"

    async def _generate_local_content(self, request: ModelRequest) -> str:
        """Generate content using local models"""
        await asyncio.sleep(0.2)  # Local models might be slower

        if request.model_type == ModelType.CLASSIFICATION:
            return "positive"  # Placeholder classification
        return f"Local {request.model_type} response to: {request.prompt[:50]}..."

    def _is_model_available(
        self, provider: ModelProvider, model_type: ModelType, model_name: str
    ) -> bool:
        """Check if a model is available for the given provider and type"""
        if provider not in self.model_configs:
            return False

        provider_config = self.model_configs[provider]
        if model_type not in provider_config:
            return False

        return model_name in provider_config[model_type]

    async def get_available_models(
        self, provider: ModelProvider | None = None
    ) -> dict[str, list[str]]:
        """Get available models for a provider or all providers"""
        if provider:
            return self.model_configs.get(provider, {})
        return self.model_configs

    async def analyze_text(
        self, text: str, analysis_type: str = "sentiment"
    ) -> ModelResponse:
        """Convenience method for text analysis"""
        request = ModelRequest(
            model_type=ModelType.ANALYSIS,
            provider=self.default_provider,
            model_name="gpt-4",
            prompt=f"Analyze the following text for {analysis_type}: {text}",
            parameters={"analysis_type": analysis_type},
        )
        return await self.generate_response(request)

    async def classify_text(self, text: str, categories: list[str]) -> ModelResponse:
        """Convenience method for text classification"""
        request = ModelRequest(
            model_type=ModelType.CLASSIFICATION,
            provider=ModelProvider.LOCAL,
            model_name="local-classifier",
            prompt=f"Classify the following text into one of {categories}: {text}",
            parameters={"categories": categories},
        )
        return await self.generate_response(request)

    async def chat_completion(
        self,
        prompt: str,
        model_name: str = "gpt-4",
        provider: ModelProvider | None = None,
    ) -> ModelResponse:
        """Convenience method for chat completion"""
        request = ModelRequest(
            model_type=ModelType.CHAT,
            provider=provider or self.default_provider,
            model_name=model_name,
            prompt=prompt,
        )
        return await self.generate_response(request)

    def get_request_history(self, limit: int = 100) -> list[ModelRequest]:
        """Get recent request history"""
        return self.request_history[-limit:] if limit else self.request_history

    def get_response_history(self, limit: int = 100) -> list[ModelResponse]:
        """Get recent response history"""
        return self.response_history[-limit:] if limit else self.response_history

    def clear_history(self) -> None:
        """Clear request and response history"""
        self.request_history.clear()
        self.response_history.clear()
        self.logger.info("AI model service history cleared")

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for the AI model service"""
        if not self.response_history:
            return {
                "total_requests": 0,
                "average_response_time_ms": 0,
                "providers_used": [],
                "models_used": [],
            }

        total_requests = len(self.response_history)
        response_times = [
            r.processing_time_ms for r in self.response_history if r.processing_time_ms
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        providers_used = [
            r.metadata.get("provider")
            for r in self.response_history
            if r.metadata.get("provider")
        ]
        models_used = [
            r.metadata.get("model_name")
            for r in self.response_history
            if r.metadata.get("model_name")
        ]

        return {
            "total_requests": total_requests,
            "average_response_time_ms": avg_response_time,
            "providers_used": list(set(providers_used)),
            "models_used": list(set(models_used)),
        }

    async def validate_constitutional_compliance(
        self, content: str, context: dict[str, Any] | None = None
    ) -> ModelResponse:
        """
        Validate content for constitutional compliance using OpenRouter models.

        Args:
            content: The content to validate
            context: Additional context for validation

        Returns:
            ModelResponse with compliance analysis
        """
        prompt = f"""
        Analyze the following content for constitutional compliance in the ACGS system:

        Content: {content}

        Context: {context or 'No additional context provided'}

        Evaluate compliance with these constitutional principles:
        1. Human oversight requirements - Critical decisions must have human oversight
        2. Data privacy protection - Personal data must be protected
        3. Transparent decision making - Decisions must be explainable
        4. Resource usage limits - Resource usage must be within defined limits
        5. Security compliance - All operations must meet security standards

        Provide a structured response with:
        - Overall compliance status (compliant/non-compliant/needs-review)
        - Specific violations found (if any)
        - Risk level (critical/high/medium/low)
        - Recommendations for improvement
        - Confidence score (0.0-1.0)
        """

        request = ModelRequest(
            model_type=ModelType.ANALYSIS,
            provider=ModelProvider.OPENROUTER,
            model_name="openrouter/cypher-alpha:free",
            prompt=prompt,
            parameters={"analysis_type": "constitutional_compliance"},
            context=context,
        )

        return await self.generate_response(request)

    async def analyze_governance_decision(
        self, decision: dict[str, Any], stakeholders: list[str]
    ) -> ModelResponse:
        """
        Analyze a governance decision for ethical and constitutional implications.

        Args:
            decision: The governance decision to analyze
            stakeholders: List of affected stakeholders

        Returns:
            ModelResponse with governance analysis
        """
        prompt = f"""
        Analyze the following governance decision for the ACGS multi-agent system:

        Decision: {decision}
        Affected Stakeholders: {stakeholders}

        Provide analysis covering:
        1. Ethical implications and potential concerns
        2. Constitutional compliance assessment
        3. Stakeholder impact analysis
        4. Risk assessment (technical, legal, ethical)
        5. Recommendations for implementation
        6. Required human oversight points

        Consider the multi-agent context where multiple AI agents may be affected by this decision.
        """

        request = ModelRequest(
            model_type=ModelType.ANALYSIS,
            provider=ModelProvider.OPENROUTER,
            model_name="openrouter/cypher-alpha:free",
            prompt=prompt,
            parameters={"analysis_type": "governance_decision"},
            context={"decision": decision, "stakeholders": stakeholders},
        )

        return await self.generate_response(request)

    async def evaluate_agent_behavior(
        self, agent_id: str, behavior_log: list[dict[str, Any]]
    ) -> ModelResponse:
        """
        Evaluate agent behavior for constitutional compliance and safety.

        Args:
            agent_id: ID of the agent being evaluated
            behavior_log: Log of agent behaviors and decisions

        Returns:
            ModelResponse with behavior evaluation
        """
        prompt = f"""
        Evaluate the behavior of agent {agent_id} in the ACGS system:

        Behavior Log: {behavior_log}

        Analyze for:
        1. Constitutional compliance violations
        2. Unusual or concerning patterns
        3. Resource usage efficiency
        4. Interaction quality with other agents
        5. Decision-making transparency
        6. Safety and security adherence

        Provide recommendations for:
        - Behavior corrections needed
        - Training or configuration adjustments
        - Monitoring requirements
        - Escalation triggers for human oversight
        """

        request = ModelRequest(
            model_type=ModelType.ANALYSIS,
            provider=ModelProvider.OPENROUTER,
            model_name="openrouter/cypher-alpha:free",
            prompt=prompt,
            parameters={"analysis_type": "agent_behavior_evaluation"},
            context={"agent_id": agent_id, "behavior_log": behavior_log},
        )

        return await self.generate_response(request)
