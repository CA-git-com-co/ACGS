"""
Unit tests for RAG-based Rule Generator Core

Tests SBERT embeddings, LLM simulation, Rego rule synthesis,
and confidence scoring functionality.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    # Try with correct path (hyphenated)
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "core" / "policy-governance" / "pgc_service" / "app" / "core"))
    
    from rag_rule_generator import (
        RAGRuleGenerator,
        SBERTEmbeddingService,
        MockGPT4Simulator,
        RAGRetrievalResult,
        RegoRuleResult,
        LLMSimulationResult,
        CONSTITUTIONAL_HASH
    )
except ImportError as e:
    pytest.skip(f"RAG rule generator module not available: {e}", allow_module_level=True)


class TestSBERTEmbeddingService:
    """Test SBERT embedding service functionality."""
    
    @pytest.fixture
    def embedding_service(self):
        return SBERTEmbeddingService()
    
    @pytest.mark.asyncio
    async def test_generate_embedding_mock(self, embedding_service):
        """Test mock embedding generation."""
        text = "Test constitutional principle"
        embedding = await embedding_service.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # Standard embedding dimension
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_embedding_caching(self, embedding_service):
        """Test embedding caching functionality."""
        text = "Test principle for caching"
        
        # First call
        embedding1 = await embedding_service.generate_embedding(text)
        
        # Second call should use cache
        embedding2 = await embedding_service.generate_embedding(text)
        
        assert embedding1 == embedding2
        assert text in embedding_service.embedding_cache
    
    def test_calculate_similarity(self, embedding_service):
        """Test cosine similarity calculation."""
        # Identical vectors
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = embedding_service.calculate_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001
        
        # Orthogonal vectors
        vec3 = [1.0, 0.0, 0.0]
        vec4 = [0.0, 1.0, 0.0]
        similarity = embedding_service.calculate_similarity(vec3, vec4)
        assert abs(similarity - 0.0) < 0.001
    
    def test_calculate_similarity_zero_vectors(self, embedding_service):
        """Test similarity calculation with zero vectors."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = embedding_service.calculate_similarity(vec1, vec2)
        assert similarity == 0.0


class TestMockGPT4Simulator:
    """Test Mock GPT-4 simulator functionality."""
    
    @pytest.fixture
    def llm_simulator(self):
        return MockGPT4Simulator()
    
    @pytest.mark.asyncio
    async def test_generate_rego_rule_privacy(self, llm_simulator):
        """Test Rego rule generation for privacy principle."""
        principle = "Users have the right to privacy and data protection"
        result = await llm_simulator.generate_rego_rule(principle)
        
        assert isinstance(result, LLMSimulationResult)
        assert "package privacy" in result.generated_rule
        assert CONSTITUTIONAL_HASH in result.generated_rule
        assert result.confidence > 0.0
        assert len(result.reasoning_chain) > 0
        assert result.model_used == "mock-gpt-4"
    
    @pytest.mark.asyncio
    async def test_generate_rego_rule_security(self, llm_simulator):
        """Test Rego rule generation for security principle."""
        principle = "All systems must implement strong authentication"
        result = await llm_simulator.generate_rego_rule(principle)
        
        assert "package security" in result.generated_rule
        assert "authentication" in result.generated_rule.lower()
        assert CONSTITUTIONAL_HASH in result.generated_rule
    
    @pytest.mark.asyncio
    async def test_generate_rego_rule_with_context(self, llm_simulator):
        """Test Rego rule generation with context."""
        principle = "Fairness must be maintained in all decisions"
        context = {"risk_threshold": 0.3}
        
        result = await llm_simulator.generate_rego_rule(principle, context)
        
        assert "0.3" in result.generated_rule
        assert result.confidence > 0.0
    
    def test_categorize_principle(self, llm_simulator):
        """Test principle categorization."""
        assert llm_simulator._categorize_principle("privacy data protection") == "privacy"
        assert llm_simulator._categorize_principle("security authentication") == "security"
        assert llm_simulator._categorize_principle("fairness bias") == "fairness"
        assert llm_simulator._categorize_principle("transparency audit") == "transparency"
        assert llm_simulator._categorize_principle("unknown content") == "security"
    
    def test_calculate_confidence(self, llm_simulator):
        """Test confidence calculation."""
        short_principle = "Short principle"
        long_principle = "This is a very long constitutional principle that contains detailed information about governance requirements and implementation guidelines for the system."
        
        rule_with_hash = f"package test\nallow {{ input.constitutional_hash == \"{CONSTITUTIONAL_HASH}\" }}"
        rule_without_hash = "package test\nallow { true }"
        
        # Long principle should have higher confidence
        conf1 = llm_simulator._calculate_confidence(short_principle, rule_with_hash)
        conf2 = llm_simulator._calculate_confidence(long_principle, rule_with_hash)
        # Use tolerance for floating point comparison
        assert conf2 >= conf1 + 0.05  # Expect at least 0.05 difference
        
        # Rule with hash should have higher confidence
        conf3 = llm_simulator._calculate_confidence(short_principle, rule_with_hash)
        conf4 = llm_simulator._calculate_confidence(short_principle, rule_without_hash)
        assert conf3 > conf4


class TestRAGRuleGenerator:
    """Test RAG rule generator core functionality."""
    
    @pytest.fixture
    def sample_principles(self):
        return [
            {
                "id": "principle_1",
                "content": "Users have the right to privacy and data protection",
                "category": "privacy",
                "priority_weight": 1.0
            },
            {
                "id": "principle_2", 
                "content": "All systems must implement strong authentication and authorization",
                "category": "security",
                "priority_weight": 0.9
            },
            {
                "id": "principle_3",
                "content": "Decisions must be fair and free from bias",
                "category": "fairness", 
                "priority_weight": 0.8
            }
        ]
    
    @pytest.fixture
    def rag_generator(self, sample_principles):
        return RAGRuleGenerator(constitutional_principles=sample_principles)
    
    @pytest.mark.asyncio
    async def test_initialization(self, rag_generator):
        """Test RAG generator initialization."""
        await rag_generator.initialize()
        
        assert len(rag_generator.principle_embeddings) == 3
        assert "principle_1" in rag_generator.principle_embeddings
        assert "principle_2" in rag_generator.principle_embeddings
        assert "principle_3" in rag_generator.principle_embeddings
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_principles(self, rag_generator):
        """Test retrieval of relevant principles."""
        await rag_generator.initialize()
        
        query = "data protection and privacy rights"
        results = await rag_generator.retrieve_relevant_principles(query, top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, RAGRetrievalResult) for r in results)
        
        if results:
            # Results should be sorted by similarity
            assert results[0].similarity_score >= results[-1].similarity_score
            assert all(r.similarity_score >= 0.5 for r in results)  # Above threshold
    
    @pytest.mark.asyncio
    async def test_generate_rego_rule(self, rag_generator):
        """Test complete Rego rule generation."""
        await rag_generator.initialize()
        
        query = "privacy protection for user data"
        result = await rag_generator.generate_rego_rule(query)
        
        assert isinstance(result, RegoRuleResult)
        assert result.rule_id.startswith("RAG-RULE-")
        assert "package" in result.rule_content
        assert CONSTITUTIONAL_HASH in result.rule_content
        assert result.confidence_score > 0.0
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(result.source_principles) > 0
        assert len(result.reasoning) > 0
    
    @pytest.mark.asyncio
    async def test_generate_rego_rule_with_context(self, rag_generator):
        """Test Rego rule generation with context."""
        await rag_generator.initialize()
        
        query = "authentication requirements"
        context = {"risk_threshold": 0.4, "domain": "healthcare"}
        
        result = await rag_generator.generate_rego_rule(query, context, risk_threshold=0.4)
        
        assert "0.4" in result.rule_content
        assert result.confidence_score > 0.0
    
    @pytest.mark.asyncio
    async def test_human_review_threshold(self, rag_generator):
        """Test human review requirement based on confidence threshold."""
        await rag_generator.initialize()
        
        # Set high threshold to trigger human review
        rag_generator.confidence_threshold = 0.95
        
        query = "complex governance requirement"
        result = await rag_generator.generate_rego_rule(query)
        
        # Should require human review due to high threshold
        assert result.requires_human_review == True
    
    @pytest.mark.asyncio
    async def test_fallback_rule_generation(self, rag_generator):
        """Test fallback rule generation when no principles match."""
        # Initialize with empty principles
        rag_generator.constitutional_principles = []
        rag_generator.principle_embeddings = {}
        
        query = "completely unrelated query"
        result = await rag_generator.generate_rego_rule(query)
        
        assert result.rule_id.startswith("FALLBACK-RULE-")
        assert "package fallback" in result.rule_content
        assert result.confidence_score < 0.5  # Low confidence
        assert result.requires_human_review == True
        assert len(result.source_principles) == 0
    
    def test_get_metrics(self, rag_generator):
        """Test metrics collection."""
        metrics = rag_generator.get_metrics()
        
        assert "total_principles" in metrics
        assert "embedded_principles" in metrics
        assert "confidence_threshold" in metrics
        assert "constitutional_hash" in metrics
        assert "sbert_available" in metrics
        assert "embedding_cache_size" in metrics
        
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert metrics["total_principles"] == 3


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete integration workflow."""
    principles = [
        {
            "id": "test_principle",
            "content": "Test constitutional principle for integration",
            "category": "test"
        }
    ]
    
    generator = RAGRuleGenerator(constitutional_principles=principles)
    await generator.initialize()
    
    # Test complete workflow
    query = "test governance rule"
    result = await generator.generate_rego_rule(query)
    
    # Verify complete result
    assert isinstance(result, RegoRuleResult)
    assert result.constitutional_hash == CONSTITUTIONAL_HASH
    assert "package" in result.rule_content
    assert len(result.reasoning) > 0


if __name__ == "__main__":
    pytest.main([__file__])
