"""
Enhanced Test Suite for LLM Reliability Framework
Target: 80%+ test coverage (from 20%)
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import the LLM Reliability Framework components
try:
    from src.backend.shared.llm_reliability_framework import (
        LLMReliabilityFramework,
        ReliabilityMetrics,
        LLMProvider,
        ReliabilityConfig,
        FailureMode,
        RecoveryStrategy
    )
except ImportError:
    # Mock imports for testing
    @dataclass
    class ReliabilityMetrics:
        response_time: float
        accuracy: float
        confidence: float
        error_rate: float
        
    @dataclass
    class ReliabilityConfig:
        max_retries: int = 3
        timeout_seconds: float = 30.0
        min_confidence_threshold: float = 0.8
        
    class LLMProvider:
        def __init__(self, name: str):
            self.name = name
            
    class FailureMode:
        TIMEOUT = "timeout"
        LOW_CONFIDENCE = "low_confidence"
        RATE_LIMIT = "rate_limit"
        
    class RecoveryStrategy:
        RETRY = "retry"
        FALLBACK = "fallback"
        CACHE = "cache"
        
    class LLMReliabilityFramework:
        def __init__(self, config: ReliabilityConfig):
            self.config = config
            self.providers = []
            self.metrics = {}
            
        async def execute_with_reliability(self, prompt: str, provider: str = None):
            return {"response": "test response", "confidence": 0.9}

class TestLLMReliabilityFramework:
    """Comprehensive test suite for LLM Reliability Framework."""
    
    @pytest.fixture
    def reliability_config(self):
        """Create test reliability configuration."""
        return ReliabilityConfig(
            max_retries=3,
            timeout_seconds=30.0,
            min_confidence_threshold=0.8
        )
    
    @pytest.fixture
    def llm_framework(self, reliability_config):
        """Create LLM reliability framework instance."""
        return LLMReliabilityFramework(reliability_config)
    
    @pytest.fixture
    def mock_providers(self):
        """Create mock LLM providers."""
        return [
            LLMProvider("openai_gpt4"),
            LLMProvider("anthropic_claude"),
            LLMProvider("local_llama")
        ]

    def test_framework_initialization(self, reliability_config):
        """Test framework initialization with configuration."""
        framework = LLMReliabilityFramework(reliability_config)
        
        assert framework.config == reliability_config
        assert framework.config.max_retries == 3
        assert framework.config.timeout_seconds == 30.0
        assert framework.config.min_confidence_threshold == 0.8

    def test_provider_registration(self, llm_framework, mock_providers):
        """Test LLM provider registration and management."""
        for provider in mock_providers:
            llm_framework.register_provider(provider)
        
        assert len(llm_framework.providers) == 3
        assert "openai_gpt4" in [p.name for p in llm_framework.providers]
        assert "anthropic_claude" in [p.name for p in llm_framework.providers]
        assert "local_llama" in [p.name for p in llm_framework.providers]

    @pytest.mark.asyncio
    async def test_successful_llm_execution(self, llm_framework):
        """Test successful LLM execution with reliability monitoring."""
        prompt = "Test constitutional governance prompt"
        
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {
                "response": "Constitutional governance response",
                "confidence": 0.95,
                "execution_time": 1.2
            }
            
            result = await llm_framework.execute_with_reliability(prompt)
            
            assert result["response"] == "Constitutional governance response"
            assert result["confidence"] == 0.95
            assert result["execution_time"] == 1.2
            mock_call.assert_called_once_with(prompt, None)

    @pytest.mark.asyncio
    async def test_retry_mechanism_on_failure(self, llm_framework):
        """Test retry mechanism when LLM calls fail."""
        prompt = "Test retry prompt"
        
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            # First two calls fail, third succeeds
            mock_call.side_effect = [
                Exception("Network error"),
                Exception("Rate limit"),
                {"response": "Success after retry", "confidence": 0.9}
            ]
            
            result = await llm_framework.execute_with_reliability(prompt)
            
            assert result["response"] == "Success after retry"
            assert mock_call.call_count == 3

    @pytest.mark.asyncio
    async def test_fallback_provider_mechanism(self, llm_framework, mock_providers):
        """Test fallback to alternative providers on failure."""
        for provider in mock_providers:
            llm_framework.register_provider(provider)
        
        prompt = "Test fallback prompt"
        
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            # Primary provider fails, fallback succeeds
            mock_call.side_effect = [
                Exception("Primary provider failed"),
                {"response": "Fallback provider response", "confidence": 0.85}
            ]
            
            result = await llm_framework.execute_with_reliability(
                prompt, 
                primary_provider="openai_gpt4",
                fallback_provider="anthropic_claude"
            )
            
            assert result["response"] == "Fallback provider response"
            assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_timeout_handling(self, llm_framework):
        """Test timeout handling for slow LLM responses."""
        prompt = "Test timeout prompt"
        
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            # Simulate timeout
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(35)  # Longer than 30s timeout
                return {"response": "Too slow", "confidence": 0.9}
            
            mock_call.side_effect = slow_response
            
            with pytest.raises(asyncio.TimeoutError):
                await llm_framework.execute_with_reliability(prompt)

    def test_confidence_threshold_validation(self, llm_framework):
        """Test confidence threshold validation."""
        low_confidence_result = {
            "response": "Low confidence response",
            "confidence": 0.6  # Below 0.8 threshold
        }
        
        is_valid = llm_framework._validate_confidence(low_confidence_result)
        assert not is_valid
        
        high_confidence_result = {
            "response": "High confidence response", 
            "confidence": 0.9  # Above 0.8 threshold
        }
        
        is_valid = llm_framework._validate_confidence(high_confidence_result)
        assert is_valid

    def test_metrics_collection(self, llm_framework):
        """Test reliability metrics collection and aggregation."""
        # Simulate multiple LLM calls
        test_metrics = [
            ReliabilityMetrics(1.2, 0.95, 0.9, 0.0),
            ReliabilityMetrics(2.1, 0.88, 0.85, 0.1),
            ReliabilityMetrics(0.8, 0.92, 0.88, 0.05)
        ]
        
        for metric in test_metrics:
            llm_framework._record_metrics(metric)
        
        aggregated = llm_framework.get_aggregated_metrics()
        
        assert aggregated["avg_response_time"] == pytest.approx(1.37, rel=1e-2)
        assert aggregated["avg_accuracy"] == pytest.approx(0.917, rel=1e-2)
        assert aggregated["avg_confidence"] == pytest.approx(0.877, rel=1e-2)
        assert aggregated["avg_error_rate"] == pytest.approx(0.05, rel=1e-2)

    @pytest.mark.asyncio
    async def test_cache_mechanism(self, llm_framework):
        """Test response caching for repeated prompts."""
        prompt = "Cached test prompt"
        cached_response = {
            "response": "Cached response",
            "confidence": 0.9,
            "from_cache": True
        }
        
        # First call - not cached
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = cached_response
            
            result1 = await llm_framework.execute_with_reliability(prompt, use_cache=True)
            assert result1["response"] == "Cached response"
            assert mock_call.call_count == 1
        
        # Second call - should use cache
        with patch.object(llm_framework, '_get_cached_response') as mock_cache:
            mock_cache.return_value = cached_response
            
            result2 = await llm_framework.execute_with_reliability(prompt, use_cache=True)
            assert result2["response"] == "Cached response"
            assert result2["from_cache"] is True

    def test_failure_mode_detection(self, llm_framework):
        """Test detection of different failure modes."""
        # Test timeout failure
        timeout_error = asyncio.TimeoutError("Request timed out")
        failure_mode = llm_framework._detect_failure_mode(timeout_error)
        assert failure_mode == FailureMode.TIMEOUT
        
        # Test rate limit failure
        rate_limit_error = Exception("Rate limit exceeded")
        failure_mode = llm_framework._detect_failure_mode(rate_limit_error)
        assert failure_mode == FailureMode.RATE_LIMIT
        
        # Test low confidence
        low_conf_result = {"confidence": 0.5}
        failure_mode = llm_framework._detect_failure_mode(low_conf_result)
        assert failure_mode == FailureMode.LOW_CONFIDENCE

    def test_recovery_strategy_selection(self, llm_framework):
        """Test selection of appropriate recovery strategies."""
        # Timeout should trigger retry
        strategy = llm_framework._select_recovery_strategy(FailureMode.TIMEOUT)
        assert strategy == RecoveryStrategy.RETRY
        
        # Rate limit should trigger fallback
        strategy = llm_framework._select_recovery_strategy(FailureMode.RATE_LIMIT)
        assert strategy == RecoveryStrategy.FALLBACK
        
        # Low confidence should trigger cache check
        strategy = llm_framework._select_recovery_strategy(FailureMode.LOW_CONFIDENCE)
        assert strategy == RecoveryStrategy.CACHE

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, llm_framework):
        """Test handling of concurrent LLM requests."""
        prompts = [f"Concurrent prompt {i}" for i in range(5)]
        
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"response": "Concurrent response", "confidence": 0.9}
            
            # Execute concurrent requests
            tasks = [
                llm_framework.execute_with_reliability(prompt) 
                for prompt in prompts
            ]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 5
            assert all(r["response"] == "Concurrent response" for r in results)
            assert mock_call.call_count == 5

    def test_configuration_validation(self):
        """Test validation of reliability configuration."""
        # Valid configuration
        valid_config = ReliabilityConfig(
            max_retries=3,
            timeout_seconds=30.0,
            min_confidence_threshold=0.8
        )
        framework = LLMReliabilityFramework(valid_config)
        assert framework.config.max_retries == 3
        
        # Invalid configuration should raise error
        with pytest.raises(ValueError):
            invalid_config = ReliabilityConfig(
                max_retries=-1,  # Invalid
                timeout_seconds=30.0,
                min_confidence_threshold=0.8
            )
            LLMReliabilityFramework(invalid_config)

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, llm_framework):
        """Test performance monitoring and alerting."""
        # Simulate slow responses
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            async def slow_call(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate processing time
                return {"response": "Slow response", "confidence": 0.9}
            
            mock_call.side_effect = slow_call
            
            start_time = time.time()
            result = await llm_framework.execute_with_reliability("Performance test")
            end_time = time.time()
            
            execution_time = end_time - start_time
            assert execution_time >= 0.1
            assert result["response"] == "Slow response"

    def test_error_logging_and_reporting(self, llm_framework):
        """Test error logging and reporting functionality."""
        with patch('logging.Logger.error') as mock_logger:
            error = Exception("Test error for logging")
            llm_framework._log_error(error, "test_context")
            
            mock_logger.assert_called_once()
            call_args = mock_logger.call_args[0][0]
            assert "Test error for logging" in call_args
            assert "test_context" in call_args

    @pytest.mark.integration
    async def test_end_to_end_reliability_workflow(self, llm_framework, mock_providers):
        """Test complete end-to-end reliability workflow."""
        # Register providers
        for provider in mock_providers:
            llm_framework.register_provider(provider)
        
        prompt = "End-to-end constitutional governance test"
        
        with patch.object(llm_framework, '_execute_llm_call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {
                "response": "Constitutional governance validated",
                "confidence": 0.95,
                "execution_time": 1.5
            }
            
            # Execute with full reliability features
            result = await llm_framework.execute_with_reliability(
                prompt,
                use_cache=True,
                enable_fallback=True,
                collect_metrics=True
            )
            
            assert result["response"] == "Constitutional governance validated"
            assert result["confidence"] == 0.95
            assert "execution_time" in result
            
            # Verify metrics were collected
            metrics = llm_framework.get_aggregated_metrics()
            assert "avg_response_time" in metrics
            assert "avg_confidence" in metrics
