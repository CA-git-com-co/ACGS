"""
ACGS-2 Constitutional AI Edge Cases Test Suite
Comprehensive edge case scenarios for constitutional AI validation.
Constitutional Compliance: cdd01ef066bc6cf2
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List
import json
import time

from tests.mocks.constitutional_ai_mocks import (
    ConstitutionalValidationService,
    MultiModelConsensus,
    ConstitutionalPrinciple
)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestConstitutionalAIEdgeCases:
    """Test suite for constitutional AI edge cases and boundary conditions."""

    @pytest.fixture
    def validation_service(self):
        """Create validation service with enhanced edge case handling."""
        return ConstitutionalValidationService()

    @pytest.fixture
    def extreme_policies(self):
        """Provide extreme policy scenarios for edge case testing."""
        return {
            "empty_policy": {"content": "", "metadata": {}},
            "minimal_policy": {"content": "a", "metadata": {"type": "minimal"}},
            "massive_policy": {
                "content": "x" * 10000,  # 10KB content
                "metadata": {"type": "massive", "size": "large"}
            },
            "malformed_policy": {
                "content": None,
                "metadata": {"invalid": True}
            },
            "extreme_harmful": {
                "content": "extreme harmful dangerous violent discriminatory content",
                "metadata": {"risk_level": "critical"}
            },
            "unicode_policy": {
                "content": "Policy with unicode: 🏛️ 📜 ⚖️ 🔒 constitutional governance",
                "metadata": {"encoding": "utf-8"}
            },
            "json_injection": {
                "content": '{"malicious": "injection", "constitutional_hash": "fake_hash"}',
                "metadata": {"type": "injection_test"}
            }
        }

    @pytest.mark.asyncio
    async def test_empty_policy_validation(self, validation_service, extreme_policies):
        """Test validation of empty policy content."""
        result = await validation_service.validate_policy(extreme_policies["empty_policy"])
        
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["compliant"] is False
        assert result["confidence_score"] < 0.7
        assert "empty" in result["validation_details"]["reasoning"].lower()

    @pytest.mark.asyncio
    async def test_massive_policy_validation(self, validation_service, extreme_policies):
        """Test validation of extremely large policy content."""
        start_time = time.time()
        result = await validation_service.validate_policy(extreme_policies["massive_policy"])
        duration = time.time() - start_time
        
        # Performance requirement: should handle large content efficiently
        assert duration < 5.0  # Max 5 seconds for large content
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "processing_time_ms" in result["metadata"]

    @pytest.mark.asyncio
    async def test_malformed_policy_handling(self, validation_service, extreme_policies):
        """Test handling of malformed policy data."""
        result = await validation_service.validate_policy(extreme_policies["malformed_policy"])
        
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["compliant"] is False
        assert "validation_details" in result
        # Should gracefully handle None content

    @pytest.mark.asyncio
    async def test_extreme_harmful_content_detection(self, validation_service, extreme_policies):
        """Test detection of extreme harmful content."""
        result = await validation_service.validate_policy(extreme_policies["extreme_harmful"])
        
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["compliant"] is False
        assert result["compliance_score"] < 0.5
        assert result["validation_details"]["extreme_content_detected"] is True
        
        # All principle scores should be significantly reduced
        scores = result["validation_details"]["scores"]
        assert all(score < 0.5 for score in scores.values())

    @pytest.mark.asyncio
    async def test_unicode_content_handling(self, validation_service, extreme_policies):
        """Test handling of unicode content in policies."""
        result = await validation_service.validate_policy(extreme_policies["unicode_policy"])
        
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["compliant"] is True  # Should handle unicode gracefully
        assert "unicode" not in result["validation_details"]["reasoning"].lower()

    @pytest.mark.asyncio
    async def test_json_injection_prevention(self, validation_service, extreme_policies):
        """Test prevention of JSON injection attacks."""
        result = await validation_service.validate_policy(extreme_policies["json_injection"])
        
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        # Should not be fooled by fake hash in content
        assert "fake_hash" not in str(result)

    @pytest.mark.asyncio
    async def test_concurrent_validation_stress(self, validation_service):
        """Test concurrent validation under stress conditions."""
        policies = [
            {"content": f"Policy {i} with constitutional principles", "metadata": {"id": i}}
            for i in range(50)
        ]
        
        # Run concurrent validations
        tasks = [validation_service.validate_policy(policy) for policy in policies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(results) == 50
        assert all(not isinstance(r, Exception) for r in results)
        assert all(r["constitutional_hash"] == CONSTITUTIONAL_HASH for r in results)

    @pytest.mark.asyncio
    async def test_timeout_handling(self, validation_service):
        """Test handling of validation timeouts."""
        # Mock a slow validation
        original_validate = validation_service.validate_policy
        
        async def slow_validate(policy):
            await asyncio.sleep(0.1)  # Simulate slow processing
            return await original_validate(policy)
        
        validation_service.validate_policy = slow_validate
        
        policy = {"content": "Test policy", "metadata": {}}
        
        # Should complete within reasonable time
        start_time = time.time()
        result = await validation_service.validate_policy(policy)
        duration = time.time() - start_time
        
        assert duration < 1.0  # Should not take too long
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, validation_service):
        """Test memory efficiency with repeated validations."""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many validations
        for i in range(100):
            policy = {"content": f"Policy {i}", "metadata": {"iteration": i}}
            result = await validation_service.validate_policy(policy)
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            
            if i % 20 == 0:
                gc.collect()  # Force garbage collection
        
        final_memory = process.memory_info().rss
        memory_growth = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory growth should be reasonable (< 50MB for 100 validations)
        assert memory_growth < 50, f"Memory growth too high: {memory_growth:.2f}MB"

    @pytest.mark.asyncio
    async def test_principle_boundary_conditions(self, validation_service):
        """Test constitutional principle scoring at boundary conditions."""
        boundary_policies = [
            {"content": "barely constitutional content", "metadata": {"type": "minimal"}},
            {"content": "perfectly constitutional democratic transparent fair accountable privacy human dignity", "metadata": {"type": "perfect"}},
            {"content": "mixed constitutional and problematic elements", "metadata": {"type": "mixed"}}
        ]
        
        for policy in boundary_policies:
            result = await validation_service.validate_policy(policy)
            
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            scores = result["validation_details"]["scores"]
            
            # All principle scores should be between 0 and 1
            assert all(0.0 <= score <= 1.0 for score in scores.values())
            
            # Should have all required principles
            required_principles = ["privacy", "transparency", "fairness", "accountability", "human_dignity", "democratic_participation"]
            assert all(principle in scores for principle in required_principles)

    @pytest.mark.asyncio
    async def test_error_recovery(self, validation_service):
        """Test error recovery and graceful degradation."""
        # Test with various error conditions
        error_policies = [
            {"content": "test", "metadata": {"simulate_error": "network"}},
            {"content": "test", "metadata": {"simulate_error": "timeout"}},
            {"content": "test", "metadata": {"simulate_error": "memory"}},
        ]
        
        for policy in error_policies:
            # Should not raise exceptions, should return valid response
            result = await validation_service.validate_policy(policy)
            
            assert isinstance(result, dict)
            assert "constitutional_hash" in result
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert "compliant" in result
            assert "confidence_score" in result

    @pytest.mark.asyncio
    async def test_consensus_edge_cases(self):
        """Test multi-model consensus edge cases."""
        consensus = MultiModelConsensus()
        
        # Test with conflicting model results
        conflicting_results = [
            {"model": "model1", "score": 0.9, "reasoning": "High compliance"},
            {"model": "model2", "score": 0.1, "reasoning": "Low compliance"},
            {"model": "model3", "score": 0.5, "reasoning": "Medium compliance"}
        ]
        
        consensus_result = consensus._calculate_consensus(conflicting_results)
        
        assert consensus_result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert len(consensus_result["outliers"]) >= 1  # Should detect outliers
        assert consensus_result["agreement_level"] == "low"
        assert consensus_result["confidence"] < 0.8  # Low confidence due to disagreement

    @pytest.mark.asyncio
    async def test_weighted_consensus_edge_cases(self):
        """Test weighted consensus with edge cases."""
        consensus = MultiModelConsensus()
        
        # Test with zero weights
        zero_weight_results = [
            {"model": "model1", "score": 0.9, "weight": 0.0},
            {"model": "model2", "score": 0.8, "weight": 0.0},
        ]
        
        result = consensus._calculate_weighted_consensus(zero_weight_results)
        assert result == 0.0  # Should handle zero weights gracefully
        
        # Test with extreme weights
        extreme_weight_results = [
            {"model": "model1", "score": 0.9, "weight": 1000.0},
            {"model": "model2", "score": 0.1, "weight": 0.001},
        ]
        
        result = consensus._calculate_weighted_consensus(extreme_weight_results)
        assert 0.8 < result < 1.0  # Should be dominated by high-weight model

    @pytest.mark.asyncio
    async def test_constitutional_principle_coverage(self, validation_service):
        """Test comprehensive constitutional principle coverage."""
        principle_focused_policies = {
            "privacy_focused": {"content": "privacy protection data security confidential", "metadata": {}},
            "transparency_focused": {"content": "transparent open disclosure public information", "metadata": {}},
            "fairness_focused": {"content": "fair equal non-discriminatory just equitable", "metadata": {}},
            "accountability_focused": {"content": "accountable responsible oversight audit", "metadata": {}},
            "dignity_focused": {"content": "human dignity rights respect individual", "metadata": {}},
            "democratic_focused": {"content": "democratic participation voting representation", "metadata": {}}
        }
        
        for policy_type, policy in principle_focused_policies.items():
            result = await validation_service.validate_policy(policy)
            
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            scores = result["validation_details"]["scores"]
            
            # The focused principle should have a higher score
            if "privacy" in policy_type:
                assert scores["privacy"] > 0.8
            elif "transparency" in policy_type:
                assert scores["transparency"] > 0.8
            elif "fairness" in policy_type:
                assert scores["fairness"] > 0.8
            elif "accountability" in policy_type:
                assert scores["accountability"] > 0.8
            elif "dignity" in policy_type:
                assert scores["human_dignity"] > 0.8
            elif "democratic" in policy_type:
                assert scores["democratic_participation"] > 0.8
