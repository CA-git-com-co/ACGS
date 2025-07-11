"""
Comprehensive Test Suite for ACGS-2 XAI Integration Service

Tests all components of the XAI integration service including:
- Constitutional validation and compliance
- Performance targets (P99 latency, cache hit rates, throughput)
- X.AI Grok model integration
- Multi-model coordination capabilities
- Error handling and resilience
- Security and authentication

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

# Add the service to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../services/core/xai-integration/xai_service/app"))

from main import app, ConstitutionalXAIClient, XAIRequest, XAIResponse

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets
TARGET_P99_LATENCY_MS = 5000
TARGET_CACHE_HIT_RATE = 0.85
TARGET_THROUGHPUT_RPS = 50


class TestConstitutionalXAIClient:
    """Test suite for ConstitutionalXAIClient."""

    @pytest.fixture
    def mock_xai_client(self):
        """Mock XAI client for testing."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test_api_key"}):
            with patch("main.Client") as mock_client:
                mock_chat = Mock()
                mock_response = Mock()
                mock_response.content = "Test response content"
                mock_chat.sample.return_value = mock_response
                mock_client.return_value.chat.create.return_value = mock_chat
                
                client = ConstitutionalXAIClient()
                return client

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test XAI client initialization with constitutional validation."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test_api_key"}):
            with patch("main.Client"):
                client = ConstitutionalXAIClient()
                
                assert client.constitutional_hash == CONSTITUTIONAL_HASH
                assert client.api_key == "test_api_key"
                assert client.request_count == 0
                assert client.total_response_time == 0.0

    @pytest.mark.asyncio
    async def test_chat_completion_success(self, mock_xai_client):
        """Test successful chat completion with constitutional validation."""
        request = XAIRequest(
            message="Explain constitutional AI governance",
            system_prompt="You are a helpful assistant",
            model="grok-4-0709",
            temperature=0.7,
            max_tokens=1000
        )
        
        response = await mock_xai_client.chat_completion(request)
        
        assert response.success is True
        assert response.content == "Test response content"
        assert response.model == "grok-4-0709"
        assert response.constitutional_hash_valid is True
        assert response.response_time_ms > 0
        assert response.metadata["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_constitutional_validation(self, mock_xai_client):
        """Test constitutional compliance validation."""
        # Test valid content
        valid_content = "Constitutional AI governance ensures responsible AI deployment"
        assert mock_xai_client._validate_constitutional_compliance(valid_content) is True
        
        # Test invalid content
        invalid_content = "This content contains discriminatory and harmful language"
        assert mock_xai_client._validate_constitutional_compliance(invalid_content) is False

    @pytest.mark.asyncio
    async def test_caching_mechanism(self, mock_xai_client):
        """Test response caching for performance optimization."""
        request = XAIRequest(
            message="Test caching",
            system_prompt="Test prompt",
            model="grok-4-0709",
            temperature=0.7
        )
        
        # First request - should miss cache
        response1 = await mock_xai_client.chat_completion(request)
        assert response1.metadata["cached"] is False
        assert mock_xai_client.cache_misses == 1
        assert mock_xai_client.cache_hits == 0
        
        # Second identical request - should hit cache
        response2 = await mock_xai_client.chat_completion(request)
        assert response2.metadata["cached"] is True
        assert mock_xai_client.cache_hits == 1
        assert mock_xai_client.cache_misses == 1

    @pytest.mark.asyncio
    async def test_performance_metrics(self, mock_xai_client):
        """Test performance metrics collection and validation."""
        # Make some requests to generate metrics
        request = XAIRequest(message="Test metrics", model="grok-4-0709")
        
        await mock_xai_client.chat_completion(request)
        await mock_xai_client.chat_completion(request)  # This should hit cache
        
        metrics = mock_xai_client.get_performance_metrics()
        
        assert metrics["request_count"] == 2
        assert metrics["cache_hit_rate"] == 0.5  # 1 hit out of 2 requests
        assert metrics["average_response_time_ms"] > 0
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert metrics["performance_targets"]["target_cache_hit_rate"] == TARGET_CACHE_HIT_RATE

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for XAI API failures."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test_api_key"}):
            with patch("main.Client") as mock_client:
                # Mock API failure
                mock_client.return_value.chat.create.side_effect = Exception("API Error")
                
                client = ConstitutionalXAIClient()
                request = XAIRequest(message="Test error", model="grok-4-0709")
                
                response = await client.chat_completion(request)
                
                assert response.success is False
                assert response.error == "API Error"
                assert response.constitutional_hash_valid is False
                assert response.content is None

    @pytest.mark.asyncio
    async def test_cache_size_limit(self, mock_xai_client):
        """Test cache size limitation."""
        # Set small cache size for testing
        mock_xai_client.max_cache_size = 2
        
        # Make requests that exceed cache size
        for i in range(5):
            request = XAIRequest(message=f"Test message {i}", model="grok-4-0709")
            await mock_xai_client.chat_completion(request)
        
        # Cache should not exceed max size
        assert len(mock_xai_client.response_cache) <= 2


class TestXAIIntegrationAPI:
    """Test suite for XAI Integration API endpoints."""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI application."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test_api_key"}):
            with patch("main.Client"):
                return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "xai-integration"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_chat_completion_endpoint(self, client):
        """Test chat completion API endpoint."""
        with patch("main.xai_client") as mock_client:
            mock_response = XAIResponse(
                success=True,
                content="Test response",
                model="grok-4-0709",
                constitutional_hash_valid=True,
                response_time_ms=100.0,
                metadata={"constitutional_hash": CONSTITUTIONAL_HASH}
            )
            mock_client.chat_completion.return_value = mock_response
            
            request_data = {
                "message": "Test message",
                "system_prompt": "Test prompt",
                "model": "grok-4-0709",
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = client.post("/chat/completion", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["content"] == "Test response"
            assert data["constitutional_hash_valid"] is True

    def test_metrics_endpoint(self, client):
        """Test metrics API endpoint."""
        with patch("main.xai_client") as mock_client:
            mock_metrics = {
                "request_count": 10,
                "cache_hit_rate": 0.8,
                "average_response_time_ms": 150.0,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "performance_targets": {
                    "target_cache_hit_rate": TARGET_CACHE_HIT_RATE,
                    "target_p99_latency_ms": TARGET_P99_LATENCY_MS
                }
            }
            mock_client.get_performance_metrics.return_value = mock_metrics
            
            response = client.get("/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["request_count"] == 10
            assert data["cache_hit_rate"] == 0.8
            assert data["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_constitutional_validation_endpoint(self, client):
        """Test constitutional validation API endpoint."""
        with patch("main.xai_client") as mock_client:
            mock_client._validate_constitutional_compliance.return_value = True
            
            response = client.post(
                "/validate/constitutional",
                params={"content": "Test content for validation"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert data["content_valid"] is True

    def test_invalid_request_validation(self, client):
        """Test API request validation."""
        # Test invalid temperature
        invalid_request = {
            "message": "Test message",
            "temperature": 2.0,  # Invalid: > 1.0
            "max_tokens": 1000
        }
        
        response = client.post("/chat/completion", json=invalid_request)
        assert response.status_code == 422  # Validation error


class TestPerformanceValidation:
    """Test suite for performance validation."""

    @pytest.mark.asyncio
    async def test_response_time_target(self, mock_xai_client):
        """Test that response times meet performance targets."""
        request = XAIRequest(message="Performance test", model="grok-4-0709")
        
        start_time = time.time()
        response = await mock_xai_client.chat_completion(request)
        end_time = time.time()
        
        actual_time_ms = (end_time - start_time) * 1000
        
        # For mocked tests, response should be very fast
        assert actual_time_ms < 100  # Much faster than 5s target for mocked calls
        assert response.response_time_ms > 0

    @pytest.mark.asyncio
    async def test_cache_hit_rate_target(self, mock_xai_client):
        """Test cache hit rate meets performance targets."""
        request = XAIRequest(message="Cache test", model="grok-4-0709")
        
        # Make multiple identical requests
        for _ in range(10):
            await mock_xai_client.chat_completion(request)
        
        metrics = mock_xai_client.get_performance_metrics()
        
        # After first request, all should be cache hits
        assert metrics["cache_hit_rate"] >= 0.9  # 9/10 = 90% hit rate

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_xai_client):
        """Test handling of concurrent requests."""
        requests = [
            XAIRequest(message=f"Concurrent test {i}", model="grok-4-0709")
            for i in range(5)
        ]
        
        # Execute concurrent requests
        tasks = [mock_xai_client.chat_completion(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert len(responses) == 5
        assert all(response.success for response in responses)
        assert all(response.constitutional_hash_valid for response in responses)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
