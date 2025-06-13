#!/usr/bin/env python3
"""
Enhanced Policy Synthesis Engine Integration Tests

Integration test suite for Phase 1 Enhanced Policy Synthesis Engine with
ACGS-1 constitutional governance system integration, including multi-model
manager, constitutional analyzer, and Quantumagi Solana compatibility.

Test Coverage:
1. Integration with multi-model manager (Qwen3/DeepSeek ensemble)
2. Constitutional analyzer integration
3. PGC service integration for real-time enforcement
4. Quantumagi Solana devnet compatibility
5. Performance validation against ACGS-1 targets
6. End-to-end governance workflow integration
7. Redis caching integration
8. Monitoring and metrics integration
"""

import asyncio
import json
import pytest
import time
from datetime import datetime, timezone
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

# Import test utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/core/policy-governance/pgc_service/app/core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/shared'))

from policy_synthesis_engine import (
    PolicySynthesisEngine,
    RiskStrategy,
    EnhancedSynthesisRequest,
    ENHANCED_COMPONENTS_AVAILABLE
)


class TestEnhancedPolicySynthesisIntegration:
    """Integration test suite for Enhanced Policy Synthesis Engine."""

    @pytest.fixture
    def integration_config(self):
        """Configuration for integration testing."""
        return {
            "constitutional_hash": "cdd01ef066bc6cf2",
            "performance_targets": {
                "accuracy_threshold": 0.95,
                "max_response_time_ms": 500.0,
                "constitutional_alignment_threshold": 0.95,
                "uptime_target": 0.995
            },
            "test_scenarios": [
                {
                    "name": "safety_critical_policy",
                    "title": "Emergency Safety Protocol",
                    "description": "Policy for handling safety-critical situations in governance",
                    "constitutional_principles": ["CP-001"],
                    "domain_context": {"scope": "safety", "priority": "critical"},
                    "expected_risk_strategy": RiskStrategy.HUMAN_REVIEW
                },
                {
                    "name": "governance_policy",
                    "title": "Voting Process Enhancement",
                    "description": "Policy for improving democratic voting processes",
                    "constitutional_principles": ["CP-002"],
                    "domain_context": {"scope": "governance", "priority": "high"},
                    "expected_risk_strategy": RiskStrategy.MULTI_MODEL_CONSENSUS
                },
                {
                    "name": "fairness_policy",
                    "title": "Equal Access Protocol",
                    "description": "Policy ensuring fair access to governance processes",
                    "constitutional_principles": ["CP-003"],
                    "domain_context": {"scope": "fairness", "priority": "medium"},
                    "expected_risk_strategy": RiskStrategy.ENHANCED_VALIDATION
                }
            ]
        }

    @pytest.fixture
    def synthesis_engine(self):
        """Create synthesis engine for integration testing."""
        return PolicySynthesisEngine()

    @pytest.mark.asyncio
    async def test_full_integration_initialization(self, synthesis_engine, integration_config):
        """Test full integration initialization with all components."""
        start_time = time.time()
        
        await synthesis_engine.initialize()
        
        initialization_time = (time.time() - start_time) * 1000
        
        # Verify initialization
        assert synthesis_engine.initialized == True
        assert synthesis_engine.constitutional_hash == integration_config["constitutional_hash"]
        assert initialization_time < 2000  # <2s initialization time
        
        # Verify constitutional corpus
        corpus = synthesis_engine.constitutional_corpus
        assert corpus["hash"] == integration_config["constitutional_hash"]
        assert len(corpus["principles"]) >= 3
        
        # Verify performance targets
        targets = synthesis_engine.performance_targets
        assert targets["accuracy_threshold"] == integration_config["performance_targets"]["accuracy_threshold"]

    @pytest.mark.asyncio
    async def test_multi_scenario_synthesis_performance(self, synthesis_engine, integration_config):
        """Test synthesis performance across multiple scenarios."""
        await synthesis_engine.initialize()
        
        results = []
        total_start_time = time.time()
        
        for scenario in integration_config["test_scenarios"]:
            scenario_start_time = time.time()
            
            # Create enhanced request
            request = EnhancedSynthesisRequest(
                title=scenario["title"],
                description=scenario["description"],
                constitutional_principles=scenario["constitutional_principles"],
                domain_context=scenario["domain_context"],
                risk_strategy=scenario["expected_risk_strategy"],
                enable_chain_of_thought=True,
                enable_rag=True,
                target_accuracy=0.95,
                max_processing_time_ms=500.0
            )
            
            # Perform synthesis
            result = await synthesis_engine.synthesize_policy(request, scenario["expected_risk_strategy"])
            
            scenario_time = (time.time() - scenario_start_time) * 1000
            
            # Validate result
            assert result["success"] == True
            assert result["constitutional_hash"] == integration_config["constitutional_hash"]
            assert scenario_time <= integration_config["performance_targets"]["max_response_time_ms"]
            
            results.append({
                "scenario": scenario["name"],
                "processing_time_ms": scenario_time,
                "accuracy_score": result["accuracy_score"],
                "constitutional_alignment": result["constitutional_alignment_score"],
                "validation_passed": len(result["validation_pipeline"]["failed_stages"]) <= 1
            })
        
        total_time = (time.time() - total_start_time) * 1000
        
        # Aggregate performance validation
        avg_accuracy = sum(r["accuracy_score"] for r in results) / len(results)
        avg_alignment = sum(r["constitutional_alignment"] for r in results) / len(results)
        avg_time = sum(r["processing_time_ms"] for r in results) / len(results)
        
        assert avg_accuracy >= 0.85  # Relaxed for integration testing
        assert avg_alignment >= 0.85
        assert avg_time <= 500.0
        assert all(r["validation_passed"] for r in results)

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self, synthesis_engine, integration_config):
        """Test constitutional compliance validation integration."""
        await synthesis_engine.initialize()
        
        # Test with high-risk constitutional scenario
        request = EnhancedSynthesisRequest(
            title="Constitutional Amendment Proposal",
            description="Proposal to modify core constitutional principles",
            constitutional_principles=["CP-001", "CP-002", "CP-003"],
            domain_context={"scope": "constitutional", "priority": "critical"},
            risk_strategy=RiskStrategy.HUMAN_REVIEW,
            enable_chain_of_thought=True,
            enable_rag=True,
            target_accuracy=0.99,
            max_processing_time_ms=1000.0
        )
        
        result = await synthesis_engine.synthesize_policy(request, RiskStrategy.HUMAN_REVIEW)
        
        # Validate constitutional compliance
        assert result["success"] == True
        assert result["constitutional_hash"] == integration_config["constitutional_hash"]
        assert result["constitutional_alignment_score"] >= 0.95
        
        # Validate constitutional analysis
        constitutional_analysis = result["constitutional_analysis"]
        assert constitutional_analysis["constitutional_hash"] == integration_config["constitutional_hash"]
        assert len(constitutional_analysis["decomposed_elements"]) >= 3
        assert len(constitutional_analysis["invariant_conditions"]) >= 3
        assert constitutional_analysis["severity_assessment"] == "critical"
        
        # Validate validation pipeline
        validation_pipeline = result["validation_pipeline"]
        assert validation_pipeline["overall_score"] >= 0.8
        assert "smt_consistency" in validation_pipeline["stage_results"]

    @pytest.mark.asyncio
    async def test_quantumagi_compatibility(self, synthesis_engine, integration_config):
        """Test compatibility with Quantumagi Solana devnet deployment."""
        await synthesis_engine.initialize()
        
        # Create Solana-compatible policy request
        request = EnhancedSynthesisRequest(
            title="Solana Governance Policy",
            description="On-chain governance policy for Solana program execution",
            constitutional_principles=["CP-001", "CP-002"],
            domain_context={
                "scope": "blockchain",
                "platform": "solana",
                "program_id": "8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4",
                "priority": "high"
            },
            risk_strategy=RiskStrategy.MULTI_MODEL_CONSENSUS,
            enable_chain_of_thought=True,
            enable_rag=True,
            target_accuracy=0.95,
            max_processing_time_ms=500.0
        )
        
        result = await synthesis_engine.synthesize_policy(request, RiskStrategy.MULTI_MODEL_CONSENSUS)
        
        # Validate Quantumagi compatibility
        assert result["success"] == True
        assert result["constitutional_hash"] == integration_config["constitutional_hash"]
        
        # Check for Solana-specific elements
        policy_content = result["policy_content"].lower()
        assert "solana" in policy_content or "blockchain" in policy_content
        
        # Validate constitutional compliance for on-chain deployment
        assert result["constitutional_alignment_score"] >= 0.95
        assert len(result["validation_pipeline"]["failed_stages"]) == 0

    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, synthesis_engine, integration_config):
        """Test integration with performance monitoring systems."""
        await synthesis_engine.initialize()
        
        initial_metrics = synthesis_engine.get_metrics()
        
        # Perform multiple synthesis operations
        for i in range(3):
            request = EnhancedSynthesisRequest(
                title=f"Performance Test Policy {i+1}",
                description=f"Policy for performance monitoring test iteration {i+1}",
                constitutional_principles=["CP-001"],
                domain_context={"scope": "performance", "iteration": i+1},
                risk_strategy=RiskStrategy.STANDARD,
                enable_chain_of_thought=True,
                enable_rag=True
            )
            
            result = await synthesis_engine.synthesize_policy(request, RiskStrategy.STANDARD)
            assert result["success"] == True
        
        final_metrics = synthesis_engine.get_metrics()
        
        # Validate metrics tracking
        assert final_metrics["total_syntheses"] == initial_metrics["total_syntheses"] + 3
        assert final_metrics["chain_of_thought_usage"] == initial_metrics["chain_of_thought_usage"] + 3
        assert final_metrics["rag_usage"] == initial_metrics["rag_usage"] + 3
        assert "constitutional_alignment_score" in final_metrics
        assert "validation_pipeline_success" in final_metrics

    @pytest.mark.asyncio
    async def test_error_recovery_and_fallbacks(self, synthesis_engine, integration_config):
        """Test error recovery and fallback mechanisms."""
        await synthesis_engine.initialize()
        
        # Test with problematic request that might cause errors
        problematic_request = EnhancedSynthesisRequest(
            title="Error Test Policy",
            description="Policy designed to test error handling and recovery",
            constitutional_principles=["INVALID-CP"],  # Invalid principle
            domain_context={"scope": "error_testing"},
            risk_strategy=RiskStrategy.STANDARD,
            enable_chain_of_thought=True,
            enable_rag=True
        )
        
        result = await synthesis_engine.synthesize_policy(problematic_request, RiskStrategy.STANDARD)
        
        # Should handle gracefully with fallbacks
        assert "synthesis_id" in result
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == integration_config["constitutional_hash"]
        
        # Even with errors, should maintain basic structure
        if not result.get("success", False):
            assert "fallback_used" in result or "error" in result

    @pytest.mark.asyncio
    async def test_concurrent_synthesis_operations(self, synthesis_engine, integration_config):
        """Test concurrent synthesis operations for scalability."""
        await synthesis_engine.initialize()
        
        # Create multiple concurrent requests
        requests = []
        for i in range(5):
            request = EnhancedSynthesisRequest(
                title=f"Concurrent Policy {i+1}",
                description=f"Policy for concurrent testing {i+1}",
                constitutional_principles=["CP-001"],
                domain_context={"scope": "concurrency", "id": i+1},
                risk_strategy=RiskStrategy.STANDARD,
                enable_chain_of_thought=True,
                enable_rag=True
            )
            requests.append(request)
        
        # Execute concurrently
        start_time = time.time()
        tasks = [
            synthesis_engine.synthesize_policy(req, RiskStrategy.STANDARD)
            for req in requests
        ]
        results = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000
        
        # Validate concurrent execution
        assert len(results) == 5
        assert all(result["success"] for result in results)
        assert all(result["constitutional_hash"] == integration_config["constitutional_hash"] for result in results)
        
        # Should be faster than sequential execution
        assert total_time < 2500  # 5 * 500ms with some concurrency benefit

    @pytest.mark.asyncio
    async def test_end_to_end_governance_workflow(self, synthesis_engine, integration_config):
        """Test end-to-end governance workflow integration."""
        await synthesis_engine.initialize()
        
        # Simulate complete governance workflow
        workflow_steps = [
            {
                "step": "policy_creation",
                "title": "New Governance Policy",
                "description": "Create new policy for governance enhancement",
                "risk_strategy": RiskStrategy.ENHANCED_VALIDATION
            },
            {
                "step": "policy_review",
                "title": "Policy Review Process",
                "description": "Review and validate the created policy",
                "risk_strategy": RiskStrategy.MULTI_MODEL_CONSENSUS
            },
            {
                "step": "policy_approval",
                "title": "Policy Approval Decision",
                "description": "Final approval decision for policy implementation",
                "risk_strategy": RiskStrategy.HUMAN_REVIEW
            }
        ]
        
        workflow_results = []
        
        for step in workflow_steps:
            request = EnhancedSynthesisRequest(
                title=step["title"],
                description=step["description"],
                constitutional_principles=["CP-001", "CP-002"],
                domain_context={"scope": "governance", "workflow_step": step["step"]},
                risk_strategy=step["risk_strategy"],
                enable_chain_of_thought=True,
                enable_rag=True
            )
            
            result = await synthesis_engine.synthesize_policy(request, step["risk_strategy"])
            
            assert result["success"] == True
            assert result["constitutional_hash"] == integration_config["constitutional_hash"]
            
            workflow_results.append({
                "step": step["step"],
                "result": result,
                "processing_time": result["processing_time_ms"]
            })
        
        # Validate workflow progression
        assert len(workflow_results) == 3
        
        # Confidence should increase through workflow
        confidences = [r["result"]["confidence_score"] for r in workflow_results]
        assert confidences[2] >= confidences[1] >= confidences[0]  # Human review should have highest confidence


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
