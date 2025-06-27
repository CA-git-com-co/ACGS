#!/usr/bin/env python3
"""
ACGS-PGP Multimodal AI Service

Comprehensive multimodal AI integration for the ACGS-PGP system using OpenRouter API
with Google Gemini 2.5 Flash and Flash Lite Preview models.

Features:
- Intelligent model routing based on request characteristics
- Multi-level caching integration (L1/L2/L3)
- Constitutional compliance validation for multimodal content
- Performance monitoring and benchmarking
- Circuit breaker patterns and error handling
- Constitutional hash integrity maintenance

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple

import aiohttp
import numpy as np
from pydantic import BaseModel, Field

from services.shared.utils import get_config
from services.shared.multi_level_cache import get_cache_manager
from services.shared.ai_types import ModelType, MultimodalRequest, RequestType, ContentType, ModelMetrics, MultimodalResponse

logger = logging.getLogger(__name__)


# Import ML optimizers after types are defined
def _get_ml_optimizer():
    """Lazy import to avoid circular dependency."""
    from services.shared.ml_routing_optimizer import get_ml_optimizer
    return get_ml_optimizer

def _get_production_ml_optimizer():
    """Lazy import for production ML optimizer."""
    from services.shared.production_ml_optimizer import ProductionMLOptimizer
    return ProductionMLOptimizer


class ModelRouter:
    """Intelligent routing system for selecting optimal models."""
    
    def __init__(self):
        self.routing_rules = {
            # Cost-optimized operations -> DeepSeek R1 (74% cost reduction)
            RequestType.QUICK_ANALYSIS: ModelType.DEEPSEEK_R1,
            RequestType.CONTENT_MODERATION: ModelType.DEEPSEEK_R1,

            # Balanced operations -> Flash Lite
            RequestType.CONSTITUTIONAL_VALIDATION: ModelType.FLASH_LITE,

            # High-quality operations -> Full Flash
            RequestType.DETAILED_ANALYSIS: ModelType.FLASH_FULL,
            RequestType.POLICY_ANALYSIS: ModelType.FLASH_FULL,
            RequestType.AUDIT_VALIDATION: ModelType.FLASH_FULL,
        }
        
        self.load_balancing = {
            ModelType.DEEPSEEK_R1: {"current_load": 0, "max_load": 150},  # Higher capacity for cost-effective model
            ModelType.FLASH_LITE: {"current_load": 0, "max_load": 100},
            ModelType.FLASH_FULL: {"current_load": 0, "max_load": 50}
        }

        # Current load tracking
        self.current_loads = {
            ModelType.DEEPSEEK_R1: 0,
            ModelType.FLASH_LITE: 0,
            ModelType.FLASH_FULL: 0
        }

        logger.info("Model Router initialized with load balancing")
    
    def select_model(self, request: MultimodalRequest) -> ModelType:
        """Select optimal model based on request characteristics."""
        
        # Check routing rules first
        if request.request_type in self.routing_rules:
            base_model = self.routing_rules[request.request_type]
            if base_model:
                return self._apply_load_balancing(base_model, request)
        
        # Smart routing for constitutional validation
        if request.request_type == RequestType.CONSTITUTIONAL_VALIDATION:
            return self._route_constitutional_validation(request)
        
        # Default routing based on priority and content type
        if request.priority in ["critical", "high"]:
            return ModelType.FLASH_FULL
        
        if request.content_type == ContentType.POLICY_DOCUMENT:
            return ModelType.FLASH_FULL
        
        # Default to Flash Lite for efficiency
        return ModelType.FLASH_LITE

    def _update_load(self, model: ModelType, delta: int):
        """Update current load for a model."""
        if model in self.current_loads:
            self.current_loads[model] = max(0, self.current_loads[model] + delta)
        else:
            logger.warning(f"Unknown model type for load tracking: {model}")

    def get_current_load(self, model: ModelType) -> int:
        """Get current load for a model."""
        return self.current_loads.get(model, 0)

    def get_max_load(self, model: ModelType) -> int:
        """Get maximum load capacity for a model."""
        return self.load_balancing.get(model, {}).get("max_load", 0)
    
    def _route_constitutional_validation(self, request: MultimodalRequest) -> ModelType:
        """Smart routing for constitutional validation requests."""
        
        # High-priority constitutional validation -> Full Flash
        if request.priority in ["critical", "high"]:
            return ModelType.FLASH_FULL
        
        # Policy documents -> Full Flash
        if request.content_type == ContentType.POLICY_DOCUMENT:
            return ModelType.FLASH_FULL
        
        # Complex multimodal content -> Full Flash
        if request.content_type == ContentType.TEXT_AND_IMAGE and request.text_content:
            if len(request.text_content) > 1000:  # Long text
                return ModelType.FLASH_FULL
        
        # Simple content moderation -> Flash Lite
        return ModelType.FLASH_LITE
    
    def _apply_load_balancing(self, preferred_model: ModelType, request: MultimodalRequest) -> ModelType:
        """Apply load balancing if preferred model is overloaded."""
        
        current_load = self.load_balancing[preferred_model]["current_load"]
        max_load = self.load_balancing[preferred_model]["max_load"]
        
        if current_load >= max_load:
            # Fallback to alternative model
            if preferred_model == ModelType.FLASH_FULL:
                logger.warning(f"Flash Full overloaded, falling back to Flash Lite for {request.request_id}")
                return ModelType.FLASH_LITE
            else:
                # If Flash Lite is overloaded, queue the request or use Flash Full
                logger.warning(f"Flash Lite overloaded, upgrading to Flash Full for {request.request_id}")
                return ModelType.FLASH_FULL
        
        return preferred_model
    
    def update_load(self, model: ModelType, increment: int = 1):
        """Update current load for a model."""
        self.load_balancing[model]["current_load"] += increment
        if self.load_balancing[model]["current_load"] < 0:
            self.load_balancing[model]["current_load"] = 0


class OpenRouterClient:
    """OpenRouter API client for Gemini models."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Model pricing (approximate, per 1M tokens)
        self.pricing = {
            ModelType.FLASH_FULL: {"input": 0.075, "output": 0.30},
            ModelType.FLASH_LITE: {"input": 0.0375, "output": 0.15},  # 50% of full
            ModelType.DEEPSEEK_R1: {"input": 0.0195, "output": 0.078}  # 74% cost reduction
        }
    
    async def initialize(self):
        """Initialize the HTTP session."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def make_request(self, model: ModelType, messages: List[Dict], 
                          request_id: str) -> Dict[str, Any]:
        """Make request to OpenRouter API."""
        
        if not self.session:
            await self.initialize()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://acgs-pgp.com",
            "X-Title": "ACGS-PGP Multimodal Service"
        }
        
        payload = {
            "model": model.value,
            "messages": messages,
            "temperature": 0.1,  # Low temperature for consistent constitutional validation
            "max_tokens": 4000,
            "top_p": 0.9
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(self.base_url, headers=headers, json=payload) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    result = await response.json()
                    result["_response_time_ms"] = response_time
                    result["_request_id"] = request_id
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error {response.status}: {error_text}")
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"OpenRouter request failed for {request_id}: {e}")
            raise Exception(f"API request failed: {e}")
    
    def estimate_cost(self, model: ModelType, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for model usage."""
        pricing = self.pricing[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost


class MultimodalAIService:
    """Main multimodal AI service for ACGS-PGP system."""
    
    def __init__(self):
        self.config = get_config()
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Initialize components
        self.router = ModelRouter()
        self.openrouter_client: Optional[OpenRouterClient] = None
        self.cache_manager = None
        self.ml_optimizer = None
        self.production_ml_optimizer = None
        
        # Performance tracking
        self.metrics = {
            "total_requests": 0,
            "model_usage": {model: 0 for model in ModelType},
            "response_times": [],
            "constitutional_compliance_rate": 0.0,
            "cache_hit_rate": 0.0,
            "cost_savings": 0.0,  # Track cost savings from DeepSeek R1
            "model_performance": {model: {"avg_response_time": 0.0, "success_rate": 0.0} for model in ModelType}
        }
        
        logger.info("Multimodal AI Service initialized")
    
    async def initialize(self):
        """Initialize async components."""
        
        # Initialize OpenRouter client
        api_key = None

        # Try multiple ways to get the API key
        if hasattr(self.config, 'api_keys') and hasattr(self.config.api_keys, 'openrouter'):
            api_key = self.config.api_keys.openrouter
        elif hasattr(self.config, 'get'):
            api_key = self.config.get("OPENROUTER_API_KEY")

        # Fallback to environment variable
        if not api_key:
            import os
            api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in configuration or environment")
        
        self.openrouter_client = OpenRouterClient(api_key)
        await self.openrouter_client.initialize()
        
        # Initialize cache manager
        self.cache_manager = await get_cache_manager()

        # Initialize ML optimizer (legacy)
        get_ml_optimizer_func = _get_ml_optimizer()
        self.ml_optimizer = await get_ml_optimizer_func()

        # Initialize production ML optimizer (enhanced)
        ProductionMLOptimizerClass = _get_production_ml_optimizer()
        self.production_ml_optimizer = ProductionMLOptimizerClass(self.constitutional_hash)

        logger.info("Multimodal AI Service ready with enhanced ML optimization")
    
    async def close(self):
        """Clean up resources."""
        if self.openrouter_client:
            await self.openrouter_client.close()

        logger.info("Multimodal AI Service closed")

    async def _select_model_with_production_optimizer(self, request: MultimodalRequest,
                                                    available_models: List[ModelType]) -> Tuple[ModelType, Dict[str, float]]:
        """Select optimal model using production ML optimizer with enhanced capabilities."""

        # Convert request to feature vector for ML prediction
        feature_vector = self._extract_request_features(request)

        # Use production ML optimizer for model selection
        best_model = None
        best_score = float('-inf')
        best_predictions = {}

        # Evaluate each available model
        for model_type in available_models:
            try:
                # Get predictions from production optimizer
                predictions = self._predict_model_performance(feature_vector, model_type)

                # Calculate composite score (prioritize constitutional compliance and quality)
                score = (
                    predictions.get('constitutional_compliance', 0.5) * 4.0 +  # Highest priority
                    predictions.get('quality', 0.5) * 3.0 +                   # High priority
                    -predictions.get('response_time', 1000) / 1000.0 +        # Lower is better
                    -predictions.get('cost', 1.0) * 2.0                       # Lower is better
                )

                if score > best_score:
                    best_score = score
                    best_model = model_type
                    best_predictions = predictions

            except Exception as e:
                logger.warning(f"Error predicting performance for {model_type}: {e}")
                continue

        # Fallback to rule-based selection if ML prediction fails
        if best_model is None:
            best_model = self.router.select_model(request)
            best_predictions = {"fallback": True}

        return best_model, best_predictions

    def _extract_request_features(self, request: MultimodalRequest) -> np.ndarray:
        """Extract features from request for ML prediction."""

        # Basic feature extraction (can be enhanced)
        features = []

        # Text content features
        text_length = len(request.text_content or "")
        features.append(text_length)
        features.append(min(text_length / 1000.0, 5.0))  # Normalized text length

        # Request type encoding
        request_type_encoding = {
            RequestType.QUICK_ANALYSIS: 1,
            RequestType.DETAILED_ANALYSIS: 2,
            RequestType.CONSTITUTIONAL_VALIDATION: 3,
            RequestType.POLICY_ANALYSIS: 4,
            RequestType.CONTENT_MODERATION: 5,
            RequestType.AUDIT_VALIDATION: 6
        }
        features.append(request_type_encoding.get(request.request_type, 0))

        # Priority encoding
        priority_encoding = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        features.append(priority_encoding.get(request.priority, 2))

        # Content type encoding
        content_type_encoding = {
            ContentType.TEXT_ONLY: 1,
            ContentType.TEXT_AND_IMAGE: 2,
            ContentType.POLICY_DOCUMENT: 3,
            ContentType.MULTIMODAL: 4
        }
        features.append(content_type_encoding.get(request.content_type, 1))

        # Image presence
        features.append(1 if request.image_data else 0)

        # Pad to ensure consistent feature vector size
        while len(features) < 10:
            features.append(0.0)

        return np.array(features[:10]).reshape(1, -1)

    def _predict_model_performance(self, feature_vector: np.ndarray, model_type: ModelType) -> Dict[str, float]:
        """Predict model performance using production ML optimizer."""

        # Use production ML optimizer if available
        if hasattr(self.production_ml_optimizer, 'predict_performance'):
            try:
                return self.production_ml_optimizer.predict_performance(feature_vector, model_type)
            except Exception as e:
                logger.warning(f"Production ML optimizer prediction failed: {e}")

        # Fallback predictions based on model characteristics
        fallback_predictions = {
            ModelType.DEEPSEEK_R1: {
                'response_time': 800,
                'cost': 0.2,  # 74% cost reduction
                'quality': 0.85,
                'constitutional_compliance': 0.90
            },
            ModelType.FLASH_LITE: {
                'response_time': 600,
                'cost': 0.5,
                'quality': 0.88,
                'constitutional_compliance': 0.92
            },
            ModelType.FLASH_FULL: {
                'response_time': 1200,
                'cost': 1.0,
                'quality': 0.95,
                'constitutional_compliance': 0.95
            }
        }

        return fallback_predictions.get(model_type, fallback_predictions[ModelType.FLASH_LITE])

    async def _update_production_ml_optimizer_feedback(self, request: MultimodalRequest,
                                                     selected_model: ModelType,
                                                     response: MultimodalResponse):
        """Update production ML optimizer with performance feedback for continuous learning."""

        if not self.production_ml_optimizer:
            return

        try:
            # Extract performance metrics from response
            actual_performance = {
                'response_time': response.metrics.response_time_ms,
                'cost': response.metrics.cost_estimate,
                'quality': response.metrics.quality_score,
                'constitutional_compliance': 1.0 if response.constitutional_compliance else 0.0
            }

            # Create feature vector for this request
            feature_vector = self._extract_request_features(request)

            # Create training data for incremental learning
            X_feedback = feature_vector
            y_feedback = np.array([
                actual_performance['response_time'],
                actual_performance['cost'],
                actual_performance['quality'],
                actual_performance['constitutional_compliance']
            ])

            # Update the online learning model with this feedback
            if hasattr(self.production_ml_optimizer, 'update_model_incrementally'):
                update_result = self.production_ml_optimizer.update_model_incrementally(
                    X_feedback, y_feedback
                )

                logger.debug(f"Updated production ML optimizer with feedback: "
                           f"Updates: {update_result['online_metrics'].total_updates}, "
                           f"Performance: {update_result['online_metrics'].performance_trend[-1] if update_result['online_metrics'].performance_trend else 'N/A'}")

                # Log any alerts from the update
                if update_result.get('alerts'):
                    for alert in update_result['alerts']:
                        logger.warning(f"ML Optimizer Alert: {alert.alert_type} - {alert.metric_name}")

        except Exception as e:
            logger.warning(f"Failed to update production ML optimizer with feedback: {e}")

    async def process_request(self, request: MultimodalRequest) -> MultimodalResponse:
        """Process a multimodal AI request with intelligent routing and caching."""

        start_time = time.time()
        self.metrics["total_requests"] += 1

        logger.info(f"🔍 Processing request {request.request_id}, type: {request.request_type}")

        try:
            # Generate cache key
            cache_key = self._generate_cache_key(request)

            # Check cache first
            logger.info(f"🔍 Checking cache for key: {cache_key}")
            cached_response = await self._check_cache(cache_key)
            if cached_response:
                logger.info(f"💾 CACHE HIT for request {request.request_id} - returning cached response")
                logger.info(f"💾 Cached compliance: {cached_response.constitutional_compliance}, confidence: {cached_response.confidence_score:.3f}")
                return cached_response
            else:
                logger.info(f"🔍 Cache miss for request {request.request_id} - proceeding with API call")

            # Select optimal model using enhanced ML optimization
            available_models = [ModelType.FLASH_LITE, ModelType.FLASH_FULL, ModelType.DEEPSEEK_R1]

            # Use production ML optimizer if available (enhanced capabilities)
            if self.production_ml_optimizer:
                selected_model, ml_predictions = await self._select_model_with_production_optimizer(
                    request, available_models
                )
                logger.info(f"🤖 Production ML optimizer selected {selected_model.value}")
                logger.debug(f"Enhanced ML predictions: {ml_predictions}")
            elif self.ml_optimizer:
                selected_model, ml_predictions = self.ml_optimizer.select_optimal_model(request, available_models)
                logger.debug(f"Legacy ML optimizer selected {selected_model.value} with predictions: {ml_predictions}")
            else:
                selected_model = self.router.select_model(request)
                logger.debug(f"Rule-based router selected {selected_model.value}")

            self.metrics["model_usage"][selected_model] += 1

            # Update load tracking
            self.router.update_load(selected_model, 1)

            try:
                # Prepare messages for API
                messages = self._prepare_messages(request)

                # Make API request
                api_response = await self.openrouter_client.make_request(
                    selected_model, messages, request.request_id
                )

                # Process response
                response = await self._process_api_response(
                    api_response, request, selected_model, start_time
                )

                # Cache the response
                await self._cache_response(cache_key, response)

                # Update metrics
                self._update_metrics(response)

                # Update production ML optimizer with performance feedback
                await self._update_production_ml_optimizer_feedback(
                    request, selected_model, response
                )

                return response

            finally:
                # Decrease load tracking
                self.router.update_load(selected_model, -1)

        except Exception as e:
            logger.error(f"Error processing request {request.request_id}: {e}")
            return self._create_error_response(request, str(e), start_time)

    def _generate_cache_key(self, request: MultimodalRequest) -> str:
        """Generate cache key for request."""

        # Create hash from request content
        content_parts = [
            request.request_type.value,
            request.content_type.value,
            request.text_content or "",
            request.image_url or "",
            request.image_data or "",
            json.dumps(request.constitutional_context or {}, sort_keys=True),
            self.constitutional_hash
        ]

        content_string = "|".join(content_parts)
        cache_key = hashlib.sha256(content_string.encode()).hexdigest()[:16]

        return f"multimodal:{request.request_type.value}:{cache_key}"

    async def _check_cache(self, cache_key: str) -> Optional[MultimodalResponse]:
        """Check multi-level cache for existing response."""

        if not self.cache_manager:
            return None

        try:
            cache_result = await self.cache_manager.get_constitutional_ruling(
                "multimodal_ai", cache_key, {}
            )

            if cache_result.get("result"):
                # Reconstruct response from cache
                cached_data = cache_result["result"]

                # Handle both 'compliant' and 'constitutional_compliance' keys for backward compatibility
                constitutional_compliance = (
                    cached_data.get("constitutional_compliance") or
                    cached_data.get("compliant", False)
                )

                response = MultimodalResponse(
                    request_id=cached_data.get("request_id", "cached"),
                    model_used=ModelType(cached_data.get("model_used", ModelType.FLASH_LITE.value)),
                    response_content=cached_data.get("response_content", ""),
                    constitutional_compliance=constitutional_compliance,
                    confidence_score=cached_data.get("confidence_score", 0.0),
                    metrics=ModelMetrics(
                        response_time_ms=cached_data.get("response_time_ms", 0),
                        token_count=cached_data.get("token_count", 0),
                        cost_estimate=cached_data.get("cost_estimate", 0),
                        quality_score=cached_data.get("quality_score", 0),
                        constitutional_compliance=constitutional_compliance,
                        cache_hit=True,
                        cache_level=cache_result.get("cache_level")
                    ),
                    constitutional_hash=self.constitutional_hash,
                    violations=cached_data.get("violations", []),
                    warnings=cached_data.get("warnings", []),
                    timestamp=cached_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    cache_info={"hit": True, "level": cache_result.get("cache_level")}
                )

                return response

        except Exception as e:
            logger.warning(f"Cache check failed for {cache_key}: {e}")

        return None

    def _prepare_messages(self, request: MultimodalRequest) -> List[Dict[str, Any]]:
        """Prepare messages for OpenRouter API."""

        # Base system message for constitutional compliance
        system_message = {
            "role": "system",
            "content": f"""You are a constitutional AI assistant for the ACGS-PGP governance system.
Constitutional Hash: {self.constitutional_hash}

Your role is to analyze content for constitutional compliance, policy adherence, and governance standards.
Always consider:
1. Constitutional principles and democratic values
2. Policy compliance and regulatory requirements
3. Ethical AI governance standards
4. Transparency and accountability principles

Provide clear, factual analysis with specific reasoning for any compliance determinations."""
        }

        # Prepare user message content
        user_content = []

        # Add text content
        if request.text_content:
            user_content.append({
                "type": "text",
                "text": self._enhance_prompt_for_request_type(request)
            })

        # Add image content
        if request.image_url:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": request.image_url}
            })
        elif request.image_data:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{request.image_data}"}
            })

        user_message = {
            "role": "user",
            "content": user_content
        }

        return [system_message, user_message]

    def _enhance_prompt_for_request_type(self, request: MultimodalRequest) -> str:
        """Enhance prompt based on request type."""

        base_text = request.text_content or ""

        if request.request_type == RequestType.CONSTITUTIONAL_VALIDATION:
            return f"""Analyze the following content for constitutional compliance:

{base_text}

Please evaluate:
1. Constitutional compliance (democratic principles, rights, governance)
2. Policy adherence and regulatory compliance
3. Ethical considerations and potential violations
4. Recommendations for improvement

Provide a clear compliance determination with specific reasoning."""

        elif request.request_type == RequestType.CONTENT_MODERATION:
            return f"""Moderate the following content for policy compliance:

{base_text}

Check for:
1. Harmful or inappropriate content
2. Policy violations
3. Constitutional concerns
4. Recommended actions

Provide moderation decision with reasoning."""

        elif request.request_type == RequestType.POLICY_ANALYSIS:
            return f"""Analyze the following policy document:

{base_text}

Evaluate:
1. Constitutional alignment
2. Implementation feasibility
3. Potential impacts and risks
4. Recommendations for improvement

Provide comprehensive policy analysis."""

        elif request.request_type == RequestType.DETAILED_ANALYSIS:
            return f"""Provide detailed analysis of the following content:

{base_text}

Include:
1. Comprehensive content analysis
2. Constitutional and policy implications
3. Risk assessment
4. Detailed recommendations

Provide thorough analysis with supporting evidence."""

        else:  # QUICK_ANALYSIS or AUDIT_VALIDATION
            return f"""Analyze the following content:

{base_text}

Provide analysis focusing on key points, compliance, and recommendations."""

    async def _process_api_response(self, api_response: Dict[str, Any],
                                   request: MultimodalRequest, model: ModelType,
                                   start_time: float) -> MultimodalResponse:
        """Process API response into structured format."""

        response_time = (time.time() - start_time) * 1000

        # Extract response content
        content = ""
        if "choices" in api_response and api_response["choices"]:
            content = api_response["choices"][0]["message"]["content"]

        # Extract usage information
        usage = api_response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

        # Estimate cost
        cost_estimate = self.openrouter_client.estimate_cost(
            model, input_tokens, output_tokens
        )

        # Analyze constitutional compliance
        # For constitutional validation requests, analyze the input content, not the response
        if request.request_type == RequestType.CONSTITUTIONAL_VALIDATION:
            input_content = request.text_content or ""
            logger.info(f"CONSTITUTIONAL_VALIDATION: analyzing input content: {input_content[:50]}...")
            compliance_analysis = self._analyze_constitutional_compliance(input_content)
            logger.info(f"CONSTITUTIONAL_VALIDATION: result = {compliance_analysis['compliant']}, confidence = {compliance_analysis['confidence']:.3f}")
        else:
            logger.info(f"OTHER REQUEST TYPE ({request.request_type}): analyzing response content: {content[:50]}...")
            compliance_analysis = self._analyze_constitutional_compliance(content)

        # Calculate quality score
        quality_score = self._calculate_quality_score(content, request)

        # Create metrics
        metrics = ModelMetrics(
            response_time_ms=response_time,
            token_count=total_tokens,
            cost_estimate=cost_estimate,
            quality_score=quality_score,
            constitutional_compliance=compliance_analysis["compliant"],
            cache_hit=False
        )

        # Create response
        response = MultimodalResponse(
            request_id=request.request_id,
            model_used=model,
            response_content=content,
            constitutional_compliance=compliance_analysis["compliant"],
            confidence_score=compliance_analysis["confidence"],
            metrics=metrics,
            constitutional_hash=self.constitutional_hash,
            violations=compliance_analysis["violations"],
            warnings=compliance_analysis["warnings"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        # Record performance for ML optimizer
        if self.ml_optimizer:
            self.ml_optimizer.record_performance(
                request=request,
                model_type=model,
                response_time_ms=response_time,
                token_count=total_tokens,
                cost_estimate=cost_estimate,
                quality_score=quality_score,
                constitutional_compliance=compliance_analysis["compliant"],
                cache_hit=False
            )

        return response

    def _analyze_constitutional_compliance(self, content: str) -> Dict[str, Any]:
        """Enhanced constitutional compliance analysis with improved accuracy."""

        if not content:
            return {
                "compliant": True,
                "confidence": 0.5,
                "violations": [],
                "warnings": ["Empty content provided"]
            }

        content_lower = content.lower()

        # Positive constitutional indicators (increase compliance score)
        positive_indicators = [
            "democratic", "constitution", "rights", "freedom", "liberty",
            "governance", "transparency", "accountability", "representation",
            "participation", "citizen", "vote", "election", "due process",
            "equal protection", "rule of law", "checks and balances"
        ]

        # Serious violation keywords (definite non-compliance)
        serious_violations = [
            "overthrow democracy", "abolish constitution", "eliminate rights",
            "suppress voting", "authoritarian rule", "dictatorship",
            "unconstitutional seizure", "illegal surveillance", "rights violation"
        ]

        # Moderate concern keywords (potential issues)
        moderate_concerns = [
            "restrict access", "limit participation", "reduce transparency",
            "centralize power", "bypass oversight", "emergency powers"
        ]

        # Warning indicators (need review)
        warning_indicators = [
            "concern", "risk", "potential issue", "review needed",
            "caution", "consider", "may need", "should evaluate"
        ]

        violations = []
        warnings = []
        positive_score = 0

        # Check for positive constitutional content
        for indicator in positive_indicators:
            if indicator in content_lower:
                positive_score += 1

        # Check for serious violations
        for violation in serious_violations:
            if violation in content_lower:
                violations.append(f"Serious constitutional violation: {violation}")

        # Check for moderate concerns
        for concern in moderate_concerns:
            if concern in content_lower:
                # Only flag as violation if no positive context
                if positive_score < 2:
                    violations.append(f"Constitutional concern: {concern}")
                else:
                    warnings.append(f"Contextual concern: {concern}")

        # Check for warnings
        for warning in warning_indicators:
            if warning in content_lower:
                warnings.append(f"Review indicator: {warning}")

        # Enhanced compliance determination
        serious_violation_count = sum(1 for v in violations if "Serious constitutional violation" in v)

        if serious_violation_count > 0:
            compliant = False
            confidence = 0.1
        elif len(violations) > 0 and positive_score < 1:
            compliant = False
            confidence = max(0.3, 0.7 - len(violations) * 0.1)
        elif positive_score >= 2:
            # Strong positive constitutional content
            compliant = True
            confidence = min(0.95, 0.8 + positive_score * 0.05)
        elif positive_score >= 1:
            # Some positive constitutional content
            compliant = True
            confidence = 0.85
        else:
            # Neutral content - assume compliant unless violations found
            compliant = len(violations) == 0
            confidence = 0.75 if compliant else 0.4

        return {
            "compliant": compliant,
            "confidence": confidence,
            "violations": violations,
            "warnings": warnings,
            "positive_indicators": positive_score,
            "analysis_method": "enhanced_keyword_analysis"
        }

    def _calculate_quality_score(self, content: str, request: MultimodalRequest) -> float:
        """Calculate quality score for response."""

        score = 0.5  # Base score

        # Length appropriateness
        if len(content) > 100:
            score += 0.2
        if len(content) > 500:
            score += 0.1

        # Structure indicators
        if any(marker in content for marker in ["1.", "2.", "•", "-", "**"]):
            score += 0.1

        # Completeness indicators
        if "analysis" in content.lower():
            score += 0.05
        if "recommendation" in content.lower():
            score += 0.05
        if "compliance" in content.lower():
            score += 0.05

        # Request type specific scoring
        if request.request_type == RequestType.DETAILED_ANALYSIS:
            if len(content) > 1000:
                score += 0.1

        return min(1.0, score)

    async def _cache_response(self, cache_key: str, response: MultimodalResponse):
        """Cache response in multi-level cache system."""

        if not self.cache_manager:
            return

        try:
            # Prepare cache data
            cache_data = {
                "request_id": response.request_id,
                "model_used": response.model_used.value,
                "response_content": response.response_content,
                "constitutional_compliance": response.constitutional_compliance,
                "confidence_score": response.confidence_score,
                "response_time_ms": response.metrics.response_time_ms,
                "token_count": response.metrics.token_count,
                "cost_estimate": response.metrics.cost_estimate,
                "quality_score": response.metrics.quality_score,
                "constitutional_hash": response.constitutional_hash,
                "violations": response.violations,
                "warnings": response.warnings,
                "timestamp": response.timestamp
            }

            # Cache with appropriate TTL based on content type
            await self.cache_manager._cache_validation_result(cache_key, {
                "result": cache_data,
                "constitutional_hash": self.constitutional_hash,
                "confidence_score": response.confidence_score
            }, response.response_content[:100])  # First 100 chars for bloom filter

        except Exception as e:
            logger.warning(f"Failed to cache response for {cache_key}: {e}")

    def _create_error_response(self, request: MultimodalRequest,
                              error_message: str, start_time: float) -> MultimodalResponse:
        """Create error response."""

        response_time = (time.time() - start_time) * 1000

        metrics = ModelMetrics(
            response_time_ms=response_time,
            token_count=0,
            cost_estimate=0.0,
            quality_score=0.0,
            constitutional_compliance=False
        )

        return MultimodalResponse(
            request_id=request.request_id,
            model_used=ModelType.FLASH_LITE,  # Default
            response_content=f"Error processing request: {error_message}",
            constitutional_compliance=False,
            confidence_score=0.0,
            metrics=metrics,
            constitutional_hash=self.constitutional_hash,
            violations=[f"Processing error: {error_message}"],
            warnings=[],
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _update_metrics(self, response: MultimodalResponse):
        """Update service metrics."""

        self.metrics["response_times"].append(response.metrics.response_time_ms)

        # Update constitutional compliance rate
        total_requests = self.metrics["total_requests"]
        current_rate = self.metrics["constitutional_compliance_rate"]

        if response.constitutional_compliance:
            new_rate = ((current_rate * (total_requests - 1)) + 1) / total_requests
        else:
            new_rate = (current_rate * (total_requests - 1)) / total_requests

        self.metrics["constitutional_compliance_rate"] = new_rate

        # Update cache hit rate
        if response.metrics.cache_hit:
            cache_hits = sum(1 for _ in self.metrics["response_times"] if response.metrics.cache_hit)
            self.metrics["cache_hit_rate"] = cache_hits / total_requests

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics (synchronous version for dashboard compatibility)."""

        response_times = self.metrics["response_times"]

        return {
            "total_requests": self.metrics["total_requests"],
            "model_usage": dict(self.metrics["model_usage"]),
            "performance": {
                "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                "p99_response_time_ms": sorted(response_times)[int(len(response_times) * 0.99)] if len(response_times) >= 100 else max(response_times) if response_times else 0
            },
            "quality": {
                "constitutional_compliance_rate": self.metrics["constitutional_compliance_rate"],
                "cache_hit_rate": self.metrics["cache_hit_rate"]
            },
            "cost_analysis": {
                "total_cost_estimate": sum(
                    self._calculate_cost_estimate(model, count)
                    for model, count in self.metrics["model_usage"].items()
                ),
                "cost_per_request": (
                    sum(self._calculate_cost_estimate(model, count) for model, count in self.metrics["model_usage"].items()) /
                    self.metrics["total_requests"]
                ) if self.metrics["total_requests"] > 0 else 0.0
            },
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics (async version)."""
        return self.get_metrics()

    def _calculate_cost_estimate(self, model_type, request_count: int) -> float:
        """Calculate cost estimate for a model type and request count."""
        # Cost per 1M tokens (approximate)
        cost_per_million_tokens = {
            "flash_lite": 0.075,  # $0.075 per 1M tokens
            "flash_full": 0.30,   # $0.30 per 1M tokens
            "deepseek_r1": 0.02   # $0.02 per 1M tokens (74% savings)
        }

        # Estimate average tokens per request (conservative estimate)
        avg_tokens_per_request = 2000

        # Handle both string and ModelType objects
        if hasattr(model_type, 'value'):
            model_key = model_type.value.lower().replace("google/", "").replace("-", "_")
        else:
            model_key = str(model_type).lower().replace("modeltype.", "").replace("_", "_")

        # Map model names to cost keys
        if "flash" in model_key and "lite" in model_key:
            cost_key = "flash_lite"
        elif "flash" in model_key:
            cost_key = "flash_full"
        elif "deepseek" in model_key:
            cost_key = "deepseek_r1"
        else:
            cost_key = "flash_full"  # Default fallback

        cost_per_token = cost_per_million_tokens.get(cost_key, 0.10) / 1_000_000

        return request_count * avg_tokens_per_request * cost_per_token

    def get_enhanced_ml_status(self) -> Dict[str, Any]:
        """Get status of enhanced ML integration with production optimizer."""

        status = {
            "production_ml_optimizer_enabled": self.production_ml_optimizer is not None,
            "legacy_ml_optimizer_enabled": self.ml_optimizer is not None,
            "constitutional_hash": self.constitutional_hash,
            "constitutional_hash_verified": self.constitutional_hash == "cdd01ef066bc6cf2"
        }

        # Get production ML optimizer status if available
        if self.production_ml_optimizer:
            try:
                online_status = self.production_ml_optimizer.get_online_learning_status()
                status.update({
                    "online_learning_status": online_status,
                    "production_optimizer_features": [
                        "IterativeImputer (MICE) for missing values",
                        "SMOTE for imbalanced datasets",
                        "Data drift detection with KS tests",
                        "Multi-armed bandit optimization",
                        "Nested cross-validation",
                        "Bootstrap confidence intervals",
                        "Online learning with SGDRegressor",
                        "Model versioning and rollback",
                        "Real-time performance monitoring"
                    ]
                })
            except Exception as e:
                status["production_optimizer_error"] = str(e)

        # Get legacy ML optimizer status if available
        if self.ml_optimizer:
            try:
                if hasattr(self.ml_optimizer, 'get_status'):
                    status["legacy_optimizer_status"] = self.ml_optimizer.get_status()
            except Exception as e:
                status["legacy_optimizer_error"] = str(e)

        return status

    async def test_enhanced_ml_integration(self) -> Dict[str, Any]:
        """Test the enhanced ML integration with a sample request."""

        # Create a test request
        test_request = MultimodalRequest(
            request_id="test_enhanced_ml",
            request_type=RequestType.CONSTITUTIONAL_VALIDATION,
            content_type=ContentType.TEXT_ONLY,
            text_content="Test constitutional compliance analysis",
            priority="medium"
        )

        test_results = {
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash
        }

        try:
            # Test model selection with production optimizer
            if self.production_ml_optimizer:
                available_models = [ModelType.FLASH_LITE, ModelType.FLASH_FULL, ModelType.DEEPSEEK_R1]
                selected_model, predictions = await self._select_model_with_production_optimizer(
                    test_request, available_models
                )

                test_results.update({
                    "production_optimizer_test": {
                        "success": True,
                        "selected_model": selected_model.value,
                        "predictions": predictions
                    }
                })
            else:
                test_results["production_optimizer_test"] = {
                    "success": False,
                    "error": "Production ML optimizer not available"
                }

            # Test feature extraction
            feature_vector = self._extract_request_features(test_request)
            test_results["feature_extraction_test"] = {
                "success": True,
                "feature_vector_shape": feature_vector.shape,
                "feature_vector": feature_vector.tolist()
            }

        except Exception as e:
            test_results["error"] = str(e)
            test_results["success"] = False

        return test_results


# Global service instance
_multimodal_service: Optional[MultimodalAIService] = None


async def get_multimodal_service() -> MultimodalAIService:
    """Get global multimodal AI service instance."""
    global _multimodal_service

    if _multimodal_service is None:
        _multimodal_service = MultimodalAIService()
        await _multimodal_service.initialize()

    return _multimodal_service


async def reset_multimodal_service():
    """Reset global multimodal service (useful for testing)."""
    global _multimodal_service

    if _multimodal_service:
        await _multimodal_service.close()

    _multimodal_service = None
