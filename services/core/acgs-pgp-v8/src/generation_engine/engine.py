"""
Generation Engine

Quantum-inspired policy generation engine with constitutional compliance validation.
Integrates with ACGS-1 multi-model LLM ensemble and provides fault-tolerant policy generation.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from pydantic import BaseModel, Field, validator

from .models import LSU, Representation, RepresentationSet, RepresentationType

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """
    Configuration for the Generation Engine with validation and serialization.
    
    Provides comprehensive configuration management for policy generation
    with constitutional compliance and performance optimization.
    """
    
    # Core generation parameters
    max_policy_length: int = 5000
    min_constitutional_compliance: float = 0.8
    fault_tolerance_level: int = 2
    consensus_threshold: float = 0.7
    
    # Performance parameters
    max_concurrent_generations: int = 10
    generation_timeout_seconds: int = 300
    response_time_target_ms: int = 500
    
    # Integration parameters
    gs_service_url: str = "http://localhost:8004"
    pgc_service_url: str = "http://localhost:8005"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    
    # Model ensemble parameters
    primary_model: str = "qwen3-32b"
    fallback_models: List[str] = field(default_factory=lambda: ["deepseek-chat", "qwen3-235b"])
    consensus_strategy: str = "weighted_average"
    
    # Quantum-inspired parameters
    quantum_error_correction: bool = True
    semantic_entanglement_strength: float = 0.5
    decoherence_threshold: float = 0.1
    
    # Monitoring and logging
    enable_prometheus_metrics: bool = True
    log_level: str = "INFO"
    audit_trail_enabled: bool = True
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        validations = [
            0.0 <= self.min_constitutional_compliance <= 1.0,
            0.0 <= self.consensus_threshold <= 1.0,
            0.0 <= self.semantic_entanglement_strength <= 1.0,
            0.0 <= self.decoherence_threshold <= 1.0,
            self.max_policy_length > 0,
            self.generation_timeout_seconds > 0,
            self.response_time_target_ms > 0,
            self.fault_tolerance_level >= 1,
        ]
        
        if not all(validations):
            raise ValueError("Invalid configuration parameters")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "max_policy_length": self.max_policy_length,
            "min_constitutional_compliance": self.min_constitutional_compliance,
            "fault_tolerance_level": self.fault_tolerance_level,
            "consensus_threshold": self.consensus_threshold,
            "max_concurrent_generations": self.max_concurrent_generations,
            "generation_timeout_seconds": self.generation_timeout_seconds,
            "response_time_target_ms": self.response_time_target_ms,
            "gs_service_url": self.gs_service_url,
            "pgc_service_url": self.pgc_service_url,
            "constitutional_hash": self.constitutional_hash,
            "primary_model": self.primary_model,
            "fallback_models": self.fallback_models,
            "consensus_strategy": self.consensus_strategy,
            "quantum_error_correction": self.quantum_error_correction,
            "semantic_entanglement_strength": self.semantic_entanglement_strength,
            "decoherence_threshold": self.decoherence_threshold,
            "enable_prometheus_metrics": self.enable_prometheus_metrics,
            "log_level": self.log_level,
            "audit_trail_enabled": self.audit_trail_enabled,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationConfig":
        """Create configuration from dictionary."""
        return cls(**data)
    
    def save_to_file(self, file_path: Path) -> None:
        """Save configuration to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> "GenerationConfig":
        """Load configuration from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class PolicyGenerationRequest(BaseModel):
    """Request model for policy generation."""
    
    title: str = Field(..., description="Policy title")
    description: str = Field(..., description="Policy description")
    stakeholders: List[str] = Field(default_factory=list, description="Stakeholders")
    constitutional_principles: List[str] = Field(default_factory=list, description="Relevant principles")
    priority: str = Field(default="medium", description="Policy priority")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError("Description must be at least 20 characters")
        return v.strip()


class PolicyGenerationResponse(BaseModel):
    """Response model for policy generation."""

    generation_id: str
    policy_content: str
    constitutional_compliance_score: float
    confidence_score: float
    semantic_hash: str
    generation_time_ms: float
    consensus_data: Dict[str, Any]
    recommendations: List[str]
    constitutional_hash: str = "cdd01ef066bc6cf2"
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        protected_namespaces = ()


class GenerationEngine:
    """
    Quantum-inspired policy generation engine with constitutional compliance validation.
    
    Provides fault-tolerant policy generation using multi-model LLM ensemble
    with quantum error correction and semantic fault tolerance.
    """
    
    def __init__(self, config: GenerationConfig):
        """Initialize the Generation Engine with configuration."""
        self.config = config
        self.config.validate()
        
        # Initialize HTTP client for service communication
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize metrics and monitoring
        self._generation_count = 0
        self._error_count = 0
        self._total_generation_time = 0.0
        
        # Quantum-inspired state management
        self._quantum_state_registry: Dict[str, Dict[str, Any]] = {}
        self._semantic_entanglement_map: Dict[str, List[str]] = {}
        
        logger.info(f"Generation Engine initialized with config: {self.config.to_dict()}")
    
    async def generate_policy(
        self, 
        request: PolicyGenerationRequest,
        use_quantum_enhancement: bool = True
    ) -> PolicyGenerationResponse:
        """
        Generate policy using quantum-inspired semantic fault tolerance.
        
        Args:
            request: Policy generation request
            use_quantum_enhancement: Enable quantum-inspired enhancements
            
        Returns:
            PolicyGenerationResponse with generated policy and metadata
            
        Raises:
            ValueError: If request validation fails
            RuntimeError: If generation fails after retries
        """
        start_time = time.time()
        generation_id = f"gen_{int(start_time)}_{hash(request.title) % 10000:04d}"
        
        logger.info(f"Starting policy generation: {generation_id}")
        
        try:
            # Create initial LSU from request
            initial_lsu = self._create_initial_lsu(request)
            
            # Generate multiple representations using model ensemble
            representations = await self._generate_representations(initial_lsu, request)
            
            # Apply quantum-inspired error correction if enabled
            if use_quantum_enhancement:
                representations = await self._apply_quantum_enhancement(representations)
            
            # Create representation set and achieve consensus
            rep_set = RepresentationSet(
                representations=representations,
                consensus_threshold=self.config.consensus_threshold,
                constitutional_hash=self.config.constitutional_hash
            )
            
            # Apply fault tolerance
            corrections_applied = rep_set.apply_fault_tolerance()
            logger.info(f"Applied {corrections_applied} fault tolerance corrections")
            
            # Achieve consensus
            consensus_representation = rep_set.achieve_consensus()
            if not consensus_representation:
                raise RuntimeError("Failed to achieve consensus among generated representations")
            
            # Validate constitutional compliance
            compliance_score = await self._validate_constitutional_compliance(
                consensus_representation, request
            )
            
            if compliance_score < self.config.min_constitutional_compliance:
                logger.warning(f"Low compliance score: {compliance_score}")
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                consensus_representation, rep_set
            )
            
            generation_time_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            self._generation_count += 1
            self._total_generation_time += generation_time_ms
            
            response = PolicyGenerationResponse(
                generation_id=generation_id,
                policy_content=consensus_representation.lsu.content,
                constitutional_compliance_score=compliance_score,
                confidence_score=consensus_representation.confidence_score,
                semantic_hash=consensus_representation.lsu.semantic_hash,
                generation_time_ms=generation_time_ms,
                consensus_data={
                    "consensus_achieved": True,
                    "representations_count": len(representations),
                    "corrections_applied": corrections_applied,
                    "semantic_diversity": rep_set.get_semantic_diversity(),
                },
                recommendations=recommendations,
            )
            
            logger.info(f"Policy generation completed: {generation_id} in {generation_time_ms:.2f}ms")
            return response
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Policy generation failed: {generation_id} - {str(e)}")
            raise RuntimeError(f"Policy generation failed: {str(e)}")
    
    def _create_initial_lsu(self, request: PolicyGenerationRequest) -> LSU:
        """Create initial LSU from generation request."""
        content = f"Title: {request.title}\nDescription: {request.description}"
        if request.stakeholders:
            content += f"\nStakeholders: {', '.join(request.stakeholders)}"
        if request.constitutional_principles:
            content += f"\nPrinciples: {', '.join(request.constitutional_principles)}"

        return LSU(
            content=content,
            representation_type=RepresentationType.POLICY_DRAFT,
            metadata={
                "priority": request.priority,
                "context": request.context,
                "generation_timestamp": datetime.now().isoformat(),
            }
        )

    async def _generate_representations(
        self,
        initial_lsu: LSU,
        request: PolicyGenerationRequest
    ) -> List[Representation]:
        """Generate multiple representations using model ensemble."""
        representations = []

        # Generate representation using primary model
        try:
            primary_rep = await self._generate_single_representation(
                initial_lsu, request, self.config.primary_model
            )
            representations.append(primary_rep)
        except Exception as e:
            logger.warning(f"Primary model generation failed: {e}")

        # Generate representations using fallback models
        for model in self.config.fallback_models:
            try:
                fallback_rep = await self._generate_single_representation(
                    initial_lsu, request, model
                )
                representations.append(fallback_rep)
            except Exception as e:
                logger.warning(f"Fallback model {model} generation failed: {e}")

        if not representations:
            raise RuntimeError("All model generations failed")

        return representations

    async def _generate_single_representation(
        self,
        lsu: LSU,
        request: PolicyGenerationRequest,
        model: str
    ) -> Representation:
        """Generate single representation using specified model."""
        # Mock implementation - in production, this would call the GS service
        # with the multi-model LLM ensemble

        policy_content = f"""
# {request.title}

## Description
{request.description}

## Constitutional Compliance
This policy is designed to comply with constitutional principles including:
{', '.join(request.constitutional_principles) if request.constitutional_principles else 'General constitutional governance'}

## Stakeholders
{', '.join(request.stakeholders) if request.stakeholders else 'All governance participants'}

## Implementation Guidelines
1. Ensure transparency in all policy applications
2. Maintain accountability through audit trails
3. Respect democratic participation principles
4. Uphold rule of law in enforcement

## Monitoring and Evaluation
Regular review cycles will be established to ensure ongoing compliance
with constitutional requirements and effectiveness in achieving policy objectives.

Generated using model: {model}
Constitution Hash: {self.config.constitutional_hash}
        """.strip()

        # Create LSU for generated content
        generated_lsu = LSU(
            content=policy_content,
            representation_type=RepresentationType.POLICY_DRAFT,
            metadata={
                "model": model,
                "original_lsu_hash": lsu.semantic_hash,
                "generation_timestamp": datetime.now().isoformat(),
            }
        )

        # Calculate confidence score based on model and content quality
        confidence_score = min(0.95, 0.7 + len(policy_content) / 10000.0)

        return Representation(
            lsu=generated_lsu,
            confidence_score=confidence_score,
            constitutional_hash=self.config.constitutional_hash,
            validation_status="pending"
        )

    async def _apply_quantum_enhancement(
        self,
        representations: List[Representation]
    ) -> List[Representation]:
        """Apply quantum-inspired enhancements to representations."""
        enhanced_representations = []

        for rep in representations:
            # Apply quantum error correction
            if self.config.quantum_error_correction:
                rep.lsu.apply_error_correction()

            # Calculate quantum entanglement with other representations
            entanglement_scores = []
            for other_rep in representations:
                if other_rep != rep:
                    entanglement = self._calculate_semantic_entanglement(rep, other_rep)
                    entanglement_scores.append(entanglement)

            # Update quantum state based on entanglement
            if entanglement_scores:
                avg_entanglement = sum(entanglement_scores) / len(entanglement_scores)
                rep.lsu.quantum_state["entanglement_strength"] = avg_entanglement

                # Apply decoherence if entanglement is too low
                if avg_entanglement < self.config.decoherence_threshold:
                    rep.confidence_score *= 0.9  # Reduce confidence for low entanglement

            enhanced_representations.append(rep)

        return enhanced_representations

    def _calculate_semantic_entanglement(
        self,
        rep1: Representation,
        rep2: Representation
    ) -> float:
        """Calculate quantum-inspired semantic entanglement between representations."""
        # Simplified semantic similarity calculation
        content1_words = set(rep1.lsu.content.lower().split())
        content2_words = set(rep2.lsu.content.lower().split())

        if not content1_words or not content2_words:
            return 0.0

        intersection = len(content1_words.intersection(content2_words))
        union = len(content1_words.union(content2_words))

        jaccard_similarity = intersection / union if union > 0 else 0.0

        # Apply quantum-inspired transformation
        entanglement = min(1.0, jaccard_similarity * self.config.semantic_entanglement_strength)

        return entanglement

    async def _validate_constitutional_compliance(
        self,
        representation: Representation,
        request: PolicyGenerationRequest
    ) -> float:
        """Validate constitutional compliance using PGC service."""
        try:
            # Call PGC service for constitutional validation
            response = await self.http_client.post(
                f"{self.config.pgc_service_url}/api/v1/constitutional/validate",
                json={
                    "policy_content": representation.lsu.content,
                    "constitutional_hash": self.config.constitutional_hash,
                    "validation_type": "comprehensive"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("compliance_score", 0.8)
            else:
                logger.warning(f"PGC validation failed: {response.status_code}")
                return representation.validate_constitutional_compliance()

        except Exception as e:
            logger.warning(f"Constitutional validation error: {e}")
            # Fallback to local validation
            return representation.validate_constitutional_compliance()

    async def _generate_recommendations(
        self,
        consensus_representation: Representation,
        rep_set: RepresentationSet
    ) -> List[str]:
        """Generate recommendations based on consensus and representation analysis."""
        recommendations = []

        # Compliance-based recommendations
        compliance_score = consensus_representation.lsu.constitutional_compliance_score
        if compliance_score < 0.9:
            recommendations.append(
                f"Consider enhancing constitutional compliance (current: {compliance_score:.2f})"
            )

        # Confidence-based recommendations
        if consensus_representation.confidence_score < 0.8:
            recommendations.append(
                "Consider additional stakeholder review due to moderate confidence score"
            )

        # Diversity-based recommendations
        diversity = rep_set.get_semantic_diversity()
        if diversity < 0.5:
            recommendations.append(
                "Consider expanding policy scope for better semantic coverage"
            )

        # Quantum state recommendations
        entanglement = consensus_representation.lsu.quantum_state.get("entanglement_strength", 0.0)
        if entanglement < 0.3:
            recommendations.append(
                "Policy may benefit from better integration with existing governance framework"
            )

        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "Policy meets constitutional compliance standards",
                "Consider pilot implementation before full deployment",
                "Establish monitoring metrics for policy effectiveness"
            ])

        return recommendations

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the Generation Engine."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "generation_count": self._generation_count,
                "error_count": self._error_count,
                "average_generation_time_ms": (
                    self._total_generation_time / max(1, self._generation_count)
                ),
                "error_rate": self._error_count / max(1, self._generation_count),
            },
            "configuration": {
                "constitutional_hash": self.config.constitutional_hash,
                "consensus_threshold": self.config.consensus_threshold,
                "fault_tolerance_level": self.config.fault_tolerance_level,
            },
            "dependencies": {}
        }

        # Check GS service connectivity
        try:
            response = await self.http_client.get(
                f"{self.config.gs_service_url}/health",
                timeout=5.0
            )
            health_status["dependencies"]["gs_service"] = {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            health_status["dependencies"]["gs_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check PGC service connectivity
        try:
            response = await self.http_client.get(
                f"{self.config.pgc_service_url}/health",
                timeout=5.0
            )
            health_status["dependencies"]["pgc_service"] = {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            health_status["dependencies"]["pgc_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Determine overall health
        dependency_issues = sum(
            1 for dep in health_status["dependencies"].values()
            if dep["status"] != "healthy"
        )

        if dependency_issues > 0:
            health_status["status"] = "degraded"

        if health_status["metrics"]["error_rate"] > 0.1:
            health_status["status"] = "unhealthy"

        return health_status

    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics for monitoring."""
        return {
            "generation_engine_metrics": {
                "total_generations": self._generation_count,
                "total_errors": self._error_count,
                "success_rate": 1.0 - (self._error_count / max(1, self._generation_count)),
                "average_generation_time_ms": (
                    self._total_generation_time / max(1, self._generation_count)
                ),
                "quantum_state_registry_size": len(self._quantum_state_registry),
                "semantic_entanglement_map_size": len(self._semantic_entanglement_map),
            },
            "configuration_metrics": {
                "consensus_threshold": self.config.consensus_threshold,
                "fault_tolerance_level": self.config.fault_tolerance_level,
                "max_concurrent_generations": self.config.max_concurrent_generations,
                "response_time_target_ms": self.config.response_time_target_ms,
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()
        logger.info("Generation Engine closed")
