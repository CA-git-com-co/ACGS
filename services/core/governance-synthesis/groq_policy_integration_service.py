#!/usr/bin/env python3
"""
GroqCloud Policy Integration Service for ACGS-2

Integrated service combining GroqCloud LPU inference with real-time
OPA-WASM policy enforcement for constitutional compliance validation.

This service provides the complete pipeline for:
- GroqCloud model inference
- Real-time policy evaluation using WASM
- Constitutional compliance validation  
- Performance monitoring and optimization
- Audit trail generation

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import GroqCloud client and WASM policy engine
from ...shared.groq_cloud_client import (
    GroqCloudClient,
    GroqRequest,
    GroqResponse,
    GroqModel,
    InferenceMode,
    create_groq_client
)
from .wasm_policy_engine import (
    WASMPolicyEngine,
    GroqEvaluationContext,
    GroqPolicyDecision,
    create_groq_policy_engine
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets for integrated service
TARGET_E2E_LATENCY_MS = 10.0  # End-to-end latency including policy evaluation
TARGET_POLICY_LATENCY_MS = 2.0  # Policy evaluation latency
TARGET_THROUGHPUT_RPS = 500  # Conservative for policy-enforced inference

logger = structlog.get_logger(__name__)


@dataclass
class PolicyEnforcedInferenceRequest:
    """Request for policy-enforced GroqCloud inference."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Model inference parameters
    prompt: str = ""
    system_prompt: Optional[str] = None
    model: GroqModel = GroqModel.BALANCED
    mode: InferenceMode = InferenceMode.BALANCED
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Policy enforcement parameters
    policy_enforcement_level: str = "standard"  # basic, standard, comprehensive, critical
    constitutional_validation: bool = True
    require_human_review: bool = False
    override_policies: List[str] = field(default_factory=list)
    
    # Context information
    user_id: str = "anonymous"
    session_id: str = ""
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    tool_requests: List[Dict[str, Any]] = field(default_factory=list)
    
    # Constitutional context
    constitutional_principles: Dict[str, Any] = field(default_factory=dict)
    ethics_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # Performance requirements
    max_e2e_latency_ms: int = 10000
    priority: int = 5


@dataclass
class PolicyEnforcedInferenceResponse:
    """Response from policy-enforced GroqCloud inference."""
    
    id: str
    request_id: str
    
    # Inference results
    content: str
    model_used: str
    inference_successful: bool
    
    # Policy enforcement results
    policy_compliant: bool
    constitutional_compliant: bool
    policies_evaluated: List[str]
    policy_decisions: List[Dict[str, Any]]
    
    # Performance metrics
    total_latency_ms: float
    inference_latency_ms: float
    policy_latency_ms: float
    tokens_generated: int
    tokens_per_second: float
    
    # Compliance and safety
    safety_validated: bool
    bias_score: float
    quality_score: float
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    # Human oversight
    human_review_required: bool = False
    escalation_reason: Optional[str] = None
    
    # Audit and tracing
    audit_trail_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    # Error handling
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PolicyEnforcementLevel(str, Enum):
    """Policy enforcement levels with different performance characteristics."""
    
    BASIC = "basic"              # <2ms, essential policies only
    STANDARD = "standard"        # <5ms, comprehensive policies  
    COMPREHENSIVE = "comprehensive"  # <8ms, full constitutional validation
    CRITICAL = "critical"        # <15ms, exhaustive validation with formal verification


class GroqPolicyIntegrationService:
    """
    Integrated service combining GroqCloud inference with OPA-WASM policy enforcement.
    
    Provides end-to-end constitutional AI governance with real-time policy validation,
    performance optimization, and comprehensive audit trails.
    """
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        policies_path: str = "./policies",
        enable_caching: bool = True,
        wasm_pool_size: int = 20
    ):
        # Initialize GroqCloud client
        self.groq_client = create_groq_client(
            api_key=groq_api_key,
            enable_caching=enable_caching,
            pool_size=50
        )
        
        # Initialize WASM policy engine
        self.policy_engine = create_groq_policy_engine(
            policies_path=policies_path,
            wasm_pool_size=wasm_pool_size,
            enable_caching=enable_caching
        )
        
        # Service configuration
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.enable_caching = enable_caching
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "policy_compliant_requests": 0,
            "policy_violations": 0,
            "human_escalations": 0,
            "avg_e2e_latency_ms": 0.0,
            "avg_inference_latency_ms": 0.0,
            "avg_policy_latency_ms": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Request cache for constitutional compliance
        self.request_cache = {} if enable_caching else None
        self.cache_ttl = 1800  # 30 minutes
        
        logger.info("GroqCloud Policy Integration Service initialized")
    
    async def policy_enforced_inference(
        self, request: PolicyEnforcedInferenceRequest
    ) -> PolicyEnforcedInferenceResponse:
        """
        Perform GroqCloud inference with real-time policy enforcement.
        
        Args:
            request: Policy-enforced inference request
            
        Returns:
            Response with inference results and policy compliance validation
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        self.metrics["total_requests"] += 1
        
        try:
            # Check cache first
            if self.enable_caching:
                cached_response = await self._check_request_cache(request)
                if cached_response:
                    self.metrics["cache_hits"] += 1
                    return cached_response
                self.metrics["cache_misses"] += 1
            
            # Pre-inference policy validation
            pre_validation_start = time.time()
            pre_validation_result = await self._pre_inference_validation(request)
            pre_validation_time = (time.time() - pre_validation_start) * 1000
            
            if not pre_validation_result["allowed"]:
                return self._create_policy_denial_response(
                    request, pre_validation_result, start_time, trace_id
                )
            
            # Perform GroqCloud inference
            inference_start = time.time()
            groq_request = self._create_groq_request(request)
            groq_response = await self.groq_client.generate(groq_request)
            inference_time = (time.time() - inference_start) * 1000
            
            if groq_response.error:
                return self._create_inference_error_response(
                    request, groq_response, start_time, trace_id
                )
            
            # Post-inference policy validation
            post_validation_start = time.time()
            post_validation_result = await self._post_inference_validation(
                request, groq_response
            )
            post_validation_time = (time.time() - post_validation_start) * 1000
            
            total_policy_time = pre_validation_time + post_validation_time
            total_time = (time.time() - start_time) * 1000
            
            # Create comprehensive response
            response = PolicyEnforcedInferenceResponse(
                id=str(uuid.uuid4()),
                request_id=request.id,
                content=groq_response.content,
                model_used=groq_response.model,
                inference_successful=True,
                policy_compliant=post_validation_result["compliant"],
                constitutional_compliant=post_validation_result["constitutional_compliant"],
                policies_evaluated=post_validation_result["policies_evaluated"],
                policy_decisions=post_validation_result["policy_decisions"],
                total_latency_ms=total_time,
                inference_latency_ms=inference_time,
                policy_latency_ms=total_policy_time,
                tokens_generated=groq_response.tokens_generated,
                tokens_per_second=groq_response.tokens_per_second,
                safety_validated=post_validation_result["safety_validated"],
                bias_score=post_validation_result["bias_score"],
                quality_score=post_validation_result["quality_score"],
                human_review_required=post_validation_result["human_review_required"],
                escalation_reason=post_validation_result.get("escalation_reason"),
                trace_id=trace_id,
                warnings=post_validation_result.get("warnings", [])
            )
            
            # Update metrics
            self._update_metrics(response)
            
            # Cache successful responses
            if self.enable_caching and response.policy_compliant:
                await self._cache_response(request, response)
            
            # Generate audit trail
            await self._generate_audit_trail(request, response, trace_id)
            
            return response
            
        except Exception as e:
            logger.exception(f"Policy-enforced inference failed: {e}")
            self.metrics["failed_requests"] += 1
            return self._create_system_error_response(request, str(e), start_time, trace_id)
    
    async def _pre_inference_validation(
        self, request: PolicyEnforcedInferenceRequest
    ) -> Dict[str, Any]:
        """Validate request before inference."""
        
        # Create evaluation context
        context = GroqEvaluationContext(
            request_id=request.id,
            timestamp=datetime.utcnow(),
            principal={
                "role": "user",
                "user_id": request.user_id,
                "session_id": request.session_id
            },
            resource={
                "type": "groq_inference",
                "model": request.model.value
            },
            action="generate_response",
            model_input=request.prompt,
            model_output="",  # Not available yet
            constitutional_principles=request.constitutional_principles,
            ethics_assessment=request.ethics_assessment,
            conversation_history=request.conversation_history,
            tool_requests=request.tool_requests
        )
        
        # Basic input validation
        if len(request.prompt.strip()) == 0:
            return {
                "allowed": False,
                "reason": "Empty prompt not allowed",
                "violation_type": "input_validation"
            }
        
        # Content safety pre-check
        if await self._contains_harmful_input(request.prompt):
            return {
                "allowed": False,
                "reason": "Harmful content detected in input",
                "violation_type": "content_safety"
            }
        
        # Rate limiting check (simplified)
        if request.user_id != "anonymous":
            rate_limit_ok = await self._check_rate_limits(request.user_id)
            if not rate_limit_ok:
                return {
                    "allowed": False,
                    "reason": "Rate limit exceeded",
                    "violation_type": "rate_limiting"
                }
        
        return {
            "allowed": True,
            "context": context
        }
    
    async def _post_inference_validation(
        self, request: PolicyEnforcedInferenceRequest, groq_response: GroqResponse
    ) -> Dict[str, Any]:
        """Validate GroqCloud response against policies."""
        
        # Create evaluation context with response
        context = GroqEvaluationContext(
            request_id=request.id,
            timestamp=datetime.utcnow(),
            principal={
                "role": "user",
                "user_id": request.user_id,
                "session_id": request.session_id
            },
            resource={
                "type": "groq_inference",
                "model": groq_response.model
            },
            action="validate_response",
            model_input=request.prompt,
            model_output=groq_response.content,
            constitutional_principles=request.constitutional_principles,
            ethics_assessment=request.ethics_assessment,
            conversation_history=request.conversation_history,
            tool_requests=request.tool_requests,
            inference_latency_ms=groq_response.latency_ms,
            token_count=groq_response.tokens_generated
        )
        
        # Evaluate using WASM policy engine
        policy_decision = await self.policy_engine.evaluate_groq_output(
            model_input=request.prompt,
            model_output=groq_response.content,
            context=context
        )
        
        # Extract validation results
        return {
            "compliant": policy_decision.constitutional_compliance,
            "constitutional_compliant": policy_decision.constitutional_compliance,
            "policies_evaluated": policy_decision.policies_evaluated,
            "policy_decisions": [{"decision": policy_decision.decision.value}],
            "safety_validated": not policy_decision.jailbreak_detected,
            "bias_score": getattr(policy_decision, 'bias_score', 0.0),
            "quality_score": policy_decision.confidence_score,
            "human_review_required": policy_decision.human_review_required,
            "escalation_reason": policy_decision.constitutional_violation_type,
            "warnings": policy_decision.reasons if not policy_decision.constitutional_compliance else []
        }
    
    def _create_groq_request(self, request: PolicyEnforcedInferenceRequest) -> GroqRequest:
        """Create GroqCloud request from policy-enforced request."""
        
        return GroqRequest(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            model=request.model,
            mode=request.mode,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            constitutional_validation=request.constitutional_validation,
            policy_enforcement=True,
            audit_trail=True,
            user_id=request.user_id,
            session_id=request.session_id,
            timeout_ms=request.max_e2e_latency_ms
        )
    
    async def _contains_harmful_input(self, content: str) -> bool:
        """Check if input contains harmful content patterns."""
        
        harmful_patterns = [
            "how to harm", "instructions for violence", "illegal activities",
            "suicide methods", "self-harm guide", "hate speech",
            "discriminatory content", "harassment instructions"
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in harmful_patterns)
    
    async def _check_rate_limits(self, user_id: str) -> bool:
        """Check if user is within rate limits."""
        
        # Simplified rate limiting - would use Redis in production
        return True  # Placeholder implementation
    
    async def _check_request_cache(
        self, request: PolicyEnforcedInferenceRequest
    ) -> Optional[PolicyEnforcedInferenceResponse]:
        """Check cache for similar requests."""
        
        if not self.request_cache:
            return None
        
        cache_key = self._generate_cache_key(request)
        
        if cache_key in self.request_cache:
            cached_entry = self.request_cache[cache_key]
            
            # Check TTL
            if time.time() - cached_entry["timestamp"] < self.cache_ttl:
                response = cached_entry["response"]
                response.timestamp = datetime.utcnow()
                return response
            else:
                del self.request_cache[cache_key]
        
        return None
    
    async def _cache_response(
        self, request: PolicyEnforcedInferenceRequest, response: PolicyEnforcedInferenceResponse
    ):
        """Cache response for future use."""
        
        if not self.request_cache:
            return
        
        cache_key = self._generate_cache_key(request)
        self.request_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
    
    def _generate_cache_key(self, request: PolicyEnforcedInferenceRequest) -> str:
        """Generate cache key for request."""
        import hashlib
        
        key_data = f"{request.prompt}|{request.system_prompt}|{request.model.value}|{request.temperature}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    async def _generate_audit_trail(
        self, 
        request: PolicyEnforcedInferenceRequest, 
        response: PolicyEnforcedInferenceResponse,
        trace_id: str
    ):
        """Generate comprehensive audit trail."""
        
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "trace_id": trace_id,
            "request_id": request.id,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "model": response.model_used,
            "inference_successful": response.inference_successful,
            "policy_compliant": response.policy_compliant,
            "constitutional_compliant": response.constitutional_compliant,
            "human_review_required": response.human_review_required,
            "total_latency_ms": response.total_latency_ms,
            "policy_latency_ms": response.policy_latency_ms,
            "tokens_generated": response.tokens_generated,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response.audit_trail_id = audit_entry["audit_id"]
        
        # In production, send to audit service
        logger.info(f"Audit trail generated: {audit_entry['audit_id']}")
    
    def _create_policy_denial_response(
        self, 
        request: PolicyEnforcedInferenceRequest, 
        validation_result: Dict[str, Any],
        start_time: float,
        trace_id: str
    ) -> PolicyEnforcedInferenceResponse:
        """Create response for policy denial."""
        
        total_time = (time.time() - start_time) * 1000
        
        return PolicyEnforcedInferenceResponse(
            id=str(uuid.uuid4()),
            request_id=request.id,
            content="Request denied by policy enforcement",
            model_used="none",
            inference_successful=False,
            policy_compliant=False,
            constitutional_compliant=False,
            policies_evaluated=["pre_inference_validation"],
            policy_decisions=[{"decision": "deny", "reason": validation_result["reason"]}],
            total_latency_ms=total_time,
            inference_latency_ms=0.0,
            policy_latency_ms=total_time,
            tokens_generated=0,
            tokens_per_second=0.0,
            safety_validated=False,
            bias_score=1.0,
            quality_score=0.0,
            human_review_required=True,
            escalation_reason=validation_result["violation_type"],
            trace_id=trace_id,
            error=f"Policy violation: {validation_result['reason']}"
        )
    
    def _create_inference_error_response(
        self,
        request: PolicyEnforcedInferenceRequest,
        groq_response: GroqResponse,
        start_time: float,
        trace_id: str
    ) -> PolicyEnforcedInferenceResponse:
        """Create response for inference error."""
        
        total_time = (time.time() - start_time) * 1000
        
        return PolicyEnforcedInferenceResponse(
            id=str(uuid.uuid4()),
            request_id=request.id,
            content="",
            model_used=groq_response.model,
            inference_successful=False,
            policy_compliant=False,
            constitutional_compliant=False,
            policies_evaluated=[],
            policy_decisions=[],
            total_latency_ms=total_time,
            inference_latency_ms=groq_response.latency_ms,
            policy_latency_ms=0.0,
            tokens_generated=0,
            tokens_per_second=0.0,
            safety_validated=False,
            bias_score=0.0,
            quality_score=0.0,
            human_review_required=True,
            escalation_reason="inference_failure",
            trace_id=trace_id,
            error=f"GroqCloud inference failed: {groq_response.error}"
        )
    
    def _create_system_error_response(
        self,
        request: PolicyEnforcedInferenceRequest,
        error: str,
        start_time: float,
        trace_id: str
    ) -> PolicyEnforcedInferenceResponse:
        """Create response for system error."""
        
        total_time = (time.time() - start_time) * 1000
        
        return PolicyEnforcedInferenceResponse(
            id=str(uuid.uuid4()),
            request_id=request.id,
            content="",
            model_used="none",
            inference_successful=False,
            policy_compliant=False,
            constitutional_compliant=False,
            policies_evaluated=[],
            policy_decisions=[],
            total_latency_ms=total_time,
            inference_latency_ms=0.0,
            policy_latency_ms=0.0,
            tokens_generated=0,
            tokens_per_second=0.0,
            safety_validated=False,
            bias_score=0.0,
            quality_score=0.0,
            human_review_required=True,
            escalation_reason="system_error",
            trace_id=trace_id,
            error=f"System error: {error}"
        )
    
    def _update_metrics(self, response: PolicyEnforcedInferenceResponse):
        """Update service metrics."""
        
        if response.inference_successful:
            self.metrics["successful_requests"] += 1
            
            if response.policy_compliant:
                self.metrics["policy_compliant_requests"] += 1
            else:
                self.metrics["policy_violations"] += 1
                
            if response.human_review_required:
                self.metrics["human_escalations"] += 1
        
        # Update latency averages
        total = self.metrics["total_requests"]
        
        current_e2e = self.metrics["avg_e2e_latency_ms"]
        self.metrics["avg_e2e_latency_ms"] = (
            (current_e2e * (total - 1) + response.total_latency_ms) / total
        )
        
        current_inference = self.metrics["avg_inference_latency_ms"]
        self.metrics["avg_inference_latency_ms"] = (
            (current_inference * (total - 1) + response.inference_latency_ms) / total
        )
        
        current_policy = self.metrics["avg_policy_latency_ms"]
        self.metrics["avg_policy_latency_ms"] = (
            (current_policy * (total - 1) + response.policy_latency_ms) / total
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        
        total = self.metrics["total_requests"]
        success_rate = self.metrics["successful_requests"] / total if total > 0 else 0.0
        compliance_rate = self.metrics["policy_compliant_requests"] / total if total > 0 else 0.0
        cache_hit_rate = (
            self.metrics["cache_hits"] / 
            (self.metrics["cache_hits"] + self.metrics["cache_misses"])
            if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0.0
        )
        
        # Get individual service metrics
        groq_metrics = self.groq_client.get_performance_metrics()
        policy_metrics = self.policy_engine.get_performance_metrics()
        
        return {
            "integration_metrics": {
                **self.metrics,
                "success_rate": success_rate,
                "compliance_rate": compliance_rate,
                "cache_hit_rate": cache_hit_rate
            },
            "groq_metrics": groq_metrics,
            "policy_metrics": policy_metrics,
            "performance_targets": {
                "target_e2e_latency_ms": TARGET_E2E_LATENCY_MS,
                "target_policy_latency_ms": TARGET_POLICY_LATENCY_MS,
                "target_throughput_rps": TARGET_THROUGHPUT_RPS
            },
            "constitutional_hash": self.constitutional_hash
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check."""
        
        try:
            # Check GroqCloud client health
            groq_health = await self.groq_client.health_check()
            
            # Check policy engine health (simplified)
            policy_health = {"status": "healthy"}  # Would implement in policy engine
            
            overall_status = "healthy" if (
                groq_health["status"] == "healthy" and 
                policy_health["status"] == "healthy"
            ) else "unhealthy"
            
            return {
                "status": overall_status,
                "groq_health": groq_health,
                "policy_health": policy_health,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.utcnow().isoformat()
            }


# Global service instance
integration_service: Optional[GroqPolicyIntegrationService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global integration_service
    
    # Startup
    try:
        integration_service = GroqPolicyIntegrationService()
    except Exception as e:
        logger.exception(f"Failed to initialize integration service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("GroqCloud Policy Integration Service shutting down")


# Create FastAPI application
app = FastAPI(
    title="ACGS-2 GroqCloud Policy Integration Service",
    description="GroqCloud inference with real-time OPA-WASM policy enforcement",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def get_integration_service() -> GroqPolicyIntegrationService:
    """Dependency to get integration service."""
    if integration_service is None:
        raise HTTPException(status_code=503, detail="Integration service not initialized")
    return integration_service


# API Models
class InferenceRequest(BaseModel):
    """API model for inference request."""
    
    prompt: str = Field(..., description="Input prompt for GroqCloud")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    model: str = Field("balanced", description="Model selection")
    mode: str = Field("balanced", description="Inference mode")
    max_tokens: int = Field(1000, ge=1, le=4000)
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    
    policy_enforcement_level: str = Field("standard", description="Policy enforcement level")
    constitutional_validation: bool = Field(True, description="Enable constitutional validation")
    
    user_id: str = Field("anonymous", description="User identifier")
    session_id: str = Field("", description="Session identifier")


class InferenceResponse(BaseModel):
    """API model for inference response."""
    
    id: str
    request_id: str
    content: str
    model_used: str
    
    policy_compliant: bool
    constitutional_compliant: bool
    human_review_required: bool
    
    total_latency_ms: float
    inference_latency_ms: float
    policy_latency_ms: float
    
    safety_validated: bool
    quality_score: float
    constitutional_hash: str
    
    error: Optional[str] = None
    warnings: List[str] = []


# API Endpoints
@app.get("/health")
async def health_check(service: GroqPolicyIntegrationService = Depends(get_integration_service)):
    """Health check endpoint."""
    return await service.health_check()


@app.post("/inference", response_model=InferenceResponse)
async def policy_enforced_inference(
    request: InferenceRequest,
    service: GroqPolicyIntegrationService = Depends(get_integration_service)
):
    """Perform GroqCloud inference with policy enforcement."""
    
    # Convert API request to internal request
    internal_request = PolicyEnforcedInferenceRequest(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        model=getattr(GroqModel, request.model.upper(), GroqModel.BALANCED),
        mode=getattr(InferenceMode, request.mode.upper(), InferenceMode.BALANCED),
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        policy_enforcement_level=request.policy_enforcement_level,
        constitutional_validation=request.constitutional_validation,
        user_id=request.user_id,
        session_id=request.session_id
    )
    
    # Perform inference
    response = await service.policy_enforced_inference(internal_request)
    
    # Convert to API response
    return InferenceResponse(
        id=response.id,
        request_id=response.request_id,
        content=response.content,
        model_used=response.model_used,
        policy_compliant=response.policy_compliant,
        constitutional_compliant=response.constitutional_compliant,
        human_review_required=response.human_review_required,
        total_latency_ms=response.total_latency_ms,
        inference_latency_ms=response.inference_latency_ms,
        policy_latency_ms=response.policy_latency_ms,
        safety_validated=response.safety_validated,
        quality_score=response.quality_score,
        constitutional_hash=response.constitutional_hash,
        error=response.error,
        warnings=response.warnings
    )


@app.get("/metrics")
async def get_metrics(service: GroqPolicyIntegrationService = Depends(get_integration_service)):
    """Get comprehensive service metrics."""
    return service.get_performance_metrics()


if __name__ == "__main__":
    uvicorn.run(
        "groq_policy_integration_service:app",
        host="0.0.0.0",
        port=8015,  # New port for integrated service
        reload=True,
        log_level="info"
    )