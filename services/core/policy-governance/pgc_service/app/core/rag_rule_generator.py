"""
ACGS-2 RAG-based Rule Generator Core

This module implements the core RAG system with SBERT embeddings for semantic similarity,
LLM simulator (mock GPT-4), and Rego rule synthesis with confidence scoring.

Constitutional Hash: cdd01ef066bc6cf2

Key Features:
- SBERT embeddings for semantic similarity
- Mock GPT-4 LLM simulator for rule generation
- Rego rule synthesis with confidence scoring
- Constitutional principle retrieval
- Human-review fallback for low confidence rules
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Try to import SBERT, fallback to mock if not available
try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    logger.warning("sentence-transformers not available, using mock embeddings")


@dataclass
class RAGRetrievalResult:
    """Result of RAG retrieval for constitutional principles."""
    
    principle_id: str
    principle_content: str
    similarity_score: float
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegoRuleResult:
    """Result of Rego rule synthesis."""
    
    rule_id: str
    rule_content: str
    confidence_score: float
    source_principles: List[str]
    reasoning: str
    requires_human_review: bool = False
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class LLMSimulationResult:
    """Result of LLM simulation for rule generation."""
    
    generated_rule: str
    confidence: float
    reasoning_chain: List[str]
    model_used: str = "mock-gpt-4"
    processing_time_ms: float = 0.0


class SBERTEmbeddingService:
    """SBERT embedding service for semantic similarity."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_cache = {}
        
        if SBERT_AVAILABLE:
            try:
                self.model = SentenceTransformer(f"sentence-transformers/{model_name}")
                logger.info(f"SBERT model loaded: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load SBERT model: {e}")
                self.model = None
        else:
            logger.info("Using mock SBERT embeddings")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        if self.model and SBERT_AVAILABLE:
            try:
                embedding = await asyncio.to_thread(
                    lambda: self.model.encode([text])[0].tolist()
                )
            except Exception as e:
                logger.error(f"SBERT embedding failed: {e}")
                embedding = self._generate_mock_embedding(text)
        else:
            embedding = self._generate_mock_embedding(text)
        
        self.embedding_cache[text] = embedding
        return embedding
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding based on text hash."""
        # Create deterministic mock embedding based on text
        hash_val = hash(text) % 1000000
        np.random.seed(hash_val)
        embedding = np.random.normal(0, 1, 384).tolist()
        return embedding
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0


class MockGPT4Simulator:
    """Mock GPT-4 simulator for rule generation."""
    
    def __init__(self):
        self.model_name = "mock-gpt-4"
        self.response_templates = {
            "privacy": "package privacy\n\ndefault allow = false\n\nallow {\n    input.data_type != \"sensitive\"\n    input.user_consent == true\n}",
            "security": "package security\n\ndefault allow = false\n\nallow {\n    input.security_level >= \"medium\"\n    input.authentication == true\n}",
            "fairness": "package fairness\n\ndefault allow = false\n\nallow {\n    input.bias_score < 0.1\n    input.demographic_parity == true\n}",
            "transparency": "package transparency\n\ndefault allow = false\n\nallow {\n    input.explanation_available == true\n    input.audit_trail_complete == true\n}",
        }
    
    async def generate_rego_rule(
        self, 
        principle_content: str, 
        context: Dict[str, Any] = None
    ) -> LLMSimulationResult:
        """Generate Rego rule from constitutional principle."""
        start_time = time.time()
        
        # Determine rule category based on content
        category = self._categorize_principle(principle_content)
        
        # Generate rule based on category
        base_rule = self.response_templates.get(category, self.response_templates["security"])
        
        # Add principle-specific customizations
        customized_rule = self._customize_rule(base_rule, principle_content, context or {})
        
        # Calculate confidence based on content analysis
        confidence = self._calculate_confidence(principle_content, customized_rule)
        
        # Generate reasoning chain
        reasoning_chain = [
            f"Analyzed principle content: {principle_content[:100]}...",
            f"Categorized as: {category}",
            f"Applied template: {category}",
            f"Customized for specific requirements",
            f"Confidence score: {confidence:.2f}"
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        return LLMSimulationResult(
            generated_rule=customized_rule,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            model_used=self.model_name,
            processing_time_ms=processing_time
        )
    
    def _categorize_principle(self, content: str) -> str:
        """Categorize principle based on content keywords."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["privacy", "personal", "data protection"]):
            return "privacy"
        elif any(word in content_lower for word in ["security", "authentication", "authorization"]):
            return "security"
        elif any(word in content_lower for word in ["fairness", "bias", "discrimination"]):
            return "fairness"
        elif any(word in content_lower for word in ["transparency", "explanation", "audit"]):
            return "transparency"
        else:
            return "security"  # Default category
    
    def _customize_rule(self, base_rule: str, principle_content: str, context: Dict[str, Any]) -> str:
        """Customize rule based on principle content and context."""
        # Add constitutional hash validation
        rule_lines = base_rule.split('\n')
        
        # Insert constitutional compliance check
        compliance_check = f'    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"'
        
        # Find the allow block and add compliance check
        for i, line in enumerate(rule_lines):
            if "allow {" in line:
                rule_lines.insert(i + 1, compliance_check)
                break
        
        # Add context-specific conditions if provided
        if context.get("risk_threshold"):
            risk_check = f'    input.risk_score <= {context["risk_threshold"]}'
            for i, line in enumerate(rule_lines):
                if compliance_check in line:
                    rule_lines.insert(i + 1, risk_check)
                    break
        
        return '\n'.join(rule_lines)
    
    def _calculate_confidence(self, principle_content: str, generated_rule: str) -> float:
        """Calculate confidence score for generated rule."""
        base_confidence = 0.7
        
        # Boost confidence for longer, more detailed principles
        if len(principle_content) > 200:
            base_confidence += 0.1
        
        # Boost confidence if rule contains constitutional hash
        if CONSTITUTIONAL_HASH in generated_rule:
            base_confidence += 0.1
        
        # Boost confidence for structured rules
        if "package" in generated_rule and "allow" in generated_rule:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)


class RAGRuleGenerator:
    """Core RAG-based rule generator with SBERT embeddings and LLM simulation."""
    
    def __init__(self, constitutional_principles: List[Dict[str, Any]] = None):
        self.embedding_service = SBERTEmbeddingService()
        self.llm_simulator = MockGPT4Simulator()
        self.constitutional_principles = constitutional_principles or []
        self.principle_embeddings = {}
        self.confidence_threshold = 0.8  # Threshold for human review
        
        logger.info(f"RAG Rule Generator initialized with {len(self.constitutional_principles)} principles")
    
    async def initialize(self):
        """Initialize embeddings for constitutional principles."""
        logger.info("Initializing principle embeddings...")
        
        for principle in self.constitutional_principles:
            principle_id = principle.get("id", str(uuid4()))
            content = principle.get("content", "")
            
            if content:
                embedding = await self.embedding_service.generate_embedding(content)
                self.principle_embeddings[principle_id] = {
                    "embedding": embedding,
                    "content": content,
                    "metadata": principle
                }
        
        logger.info(f"Initialized {len(self.principle_embeddings)} principle embeddings")
    
    async def retrieve_relevant_principles(
        self, 
        query: str, 
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[RAGRetrievalResult]:
        """Retrieve most relevant constitutional principles for query."""
        if not self.principle_embeddings:
            await self.initialize()
        
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        similarities = []
        for principle_id, data in self.principle_embeddings.items():
            similarity = self.embedding_service.calculate_similarity(
                query_embedding, data["embedding"]
            )
            
            if similarity >= similarity_threshold:
                similarities.append((principle_id, similarity, data))
        
        # Sort by similarity and take top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        similarities = similarities[:top_k]
        
        results = []
        for principle_id, similarity, data in similarities:
            result = RAGRetrievalResult(
                principle_id=principle_id,
                principle_content=data["content"],
                similarity_score=similarity,
                embedding=data["embedding"],
                metadata=data["metadata"]
            )
            results.append(result)
        
        return results
    
    async def generate_rego_rule(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        risk_threshold: float = 0.55
    ) -> RegoRuleResult:
        """Generate Rego rule using RAG retrieval and LLM simulation."""
        start_time = time.time()
        
        # Step 1: Retrieve relevant principles
        relevant_principles = await self.retrieve_relevant_principles(query)
        
        if not relevant_principles:
            logger.warning(f"No relevant principles found for query: {query}")
            return self._generate_fallback_rule(query, context)
        
        # Step 2: Use most relevant principle for rule generation
        top_principle = relevant_principles[0]
        
        # Step 3: Generate rule using LLM simulator
        generation_context = context or {}
        generation_context["risk_threshold"] = risk_threshold
        generation_context["similarity_score"] = top_principle.similarity_score
        
        llm_result = await self.llm_simulator.generate_rego_rule(
            top_principle.principle_content, 
            generation_context
        )
        
        # Step 4: Create final result
        rule_id = f"RAG-RULE-{int(time.time())}-{str(uuid4())[:8]}"
        source_principles = [p.principle_id for p in relevant_principles]
        
        requires_human_review = llm_result.confidence < self.confidence_threshold
        
        reasoning = f"Retrieved {len(relevant_principles)} relevant principles. " + \
                   f"Top similarity: {top_principle.similarity_score:.3f}. " + \
                   f"LLM confidence: {llm_result.confidence:.3f}. " + \
                   f"Processing time: {(time.time() - start_time) * 1000:.1f}ms"
        
        return RegoRuleResult(
            rule_id=rule_id,
            rule_content=llm_result.generated_rule,
            confidence_score=llm_result.confidence,
            source_principles=source_principles,
            reasoning=reasoning,
            requires_human_review=requires_human_review,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
    
    def _generate_fallback_rule(self, query: str, context: Dict[str, Any] = None) -> RegoRuleResult:
        """Generate fallback rule when no relevant principles found."""
        rule_id = f"FALLBACK-RULE-{int(time.time())}"
        
        fallback_rule = f"""package fallback

default allow = false

allow {{
    # Fallback rule for: {query}
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.fallback_approved == true
}}"""
        
        return RegoRuleResult(
            rule_id=rule_id,
            rule_content=fallback_rule,
            confidence_score=0.3,  # Low confidence for fallback
            source_principles=[],
            reasoning=f"Fallback rule generated - no relevant principles found for: {query}",
            requires_human_review=True,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get RAG generator metrics."""
        return {
            "total_principles": len(self.constitutional_principles),
            "embedded_principles": len(self.principle_embeddings),
            "confidence_threshold": self.confidence_threshold,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "sbert_available": SBERT_AVAILABLE,
            "embedding_cache_size": len(self.embedding_service.embedding_cache)
        }
