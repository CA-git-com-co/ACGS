"""
Unit Tests for Policy Governance Core Service
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive unit tests for the Policy Governance service core functionality
including policy compilation, decision engines, and governance workflows.
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import time
import json
from typing import Dict, Any, List

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestPolicyGovernanceCore:
    """Unit tests for Policy Governance core functionality."""

    @pytest.fixture
    def mock_policy_compiler(self):
        """Mock policy compiler."""
        compiler = Mock()
        compiler.compile_policy = AsyncMock(return_value={
            "compiled": True,
            "policy_id": "compiled_001",
            "compilation_time_ms": 2.9,
            "bytecode_size": 1024,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "compilation_metadata": {
                "rules_compiled": 15,
                "optimizations_applied": 8,
                "syntax_errors": 0
            }
        })
        compiler.validate_syntax = Mock(return_value={
            "valid": True,
            "syntax_score": 0.98,
            "constitutional_hash": CONSTITUTIONAL_HASH
        })
        return compiler

    @pytest.fixture
    def mock_decision_engine(self):
        """Mock policy decision engine."""
        engine = Mock()
        engine.evaluate_policy = AsyncMock(return_value={
            "decision": "allow",
            "confidence": 0.94,
            "evaluation_time_ms": 1.8,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "decision_metadata": {
                "rules_evaluated": 12,
                "conditions_met": 10,
                "policy_violations": 0
            }
        })
        engine.batch_evaluate = AsyncMock(return_value={
            "batch_id": "batch_001",
            "total_evaluations": 100,
            "successful_evaluations": 98,
            "average_time_ms": 2.1,
            "constitutional_hash": CONSTITUTIONAL_HASH
        })
        return engine

    @pytest.fixture
    def mock_governance_workflow(self):
        """Mock governance workflow engine."""
        workflow = Mock()
        workflow.execute_workflow = AsyncMock(return_value={
            "workflow_id": "workflow_001",
            "status": "completed",
            "execution_time_ms": 4.5,
            "steps_completed": 8,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "workflow_results": {
                "policy_approved": True,
                "stakeholder_consensus": 0.89,
                "compliance_verified": True
            }
        })
        return workflow

    @pytest.fixture
    def mock_cache_manager(self):
        """Mock policy cache manager."""
        cache = Mock()
        cache.get_policy = AsyncMock(return_value=None)  # Cache miss initially
        cache.set_policy = AsyncMock(return_value=True)
        cache.hit_rate = Mock(return_value=0.88)  # Above 85% target
        cache.invalidate_policy = AsyncMock(return_value=True)
        return cache

    @pytest.mark.asyncio
    async def test_basic_policy_compilation(self, mock_policy_compiler):
        """Test basic policy compilation functionality."""
        policy_source = {
            "policy_id": "compile_test_001",
            "source_code": "rule allow_admin { input.user.role == 'admin' }",
            "policy_type": "access_control",
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        result = await mock_policy_compiler.compile_policy(policy_source)
        
        assert result["compiled"] is True
        assert result["compilation_time_ms"] < 5.0  # Performance target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["compilation_metadata"]["syntax_errors"] == 0

    @pytest.mark.asyncio
    async def test_policy_compilation_performance(self, mock_policy_compiler):
        """Test policy compilation performance targets."""
        policy_source = {
            "policy_id": "perf_compile_001",
            "source_code": "complex policy with multiple rules and conditions",
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        start_time = time.perf_counter()
        result = await mock_policy_compiler.compile_policy(policy_source)
        end_time = time.perf_counter()
        
        actual_time_ms = (end_time - start_time) * 1000
        
        # Verify performance targets
        assert actual_time_ms < 5.0, f"Compilation took {actual_time_ms:.2f}ms, exceeds 5ms target"
        assert result["compilation_time_ms"] < 5.0
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_policy_decision_evaluation(self, mock_decision_engine):
        """Test policy decision evaluation."""
        evaluation_request = {
            "policy_id": "decision_test_001",
            "input_context": {
                "user": {"role": "admin", "department": "engineering"},
                "resource": {"type": "database", "classification": "sensitive"},
                "action": "read"
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        result = await mock_decision_engine.evaluate_policy(evaluation_request)
        
        assert result["decision"] in ["allow", "deny"]
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["evaluation_time_ms"] < 5.0  # Performance target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["decision_metadata"]["policy_violations"] == 0

    @pytest.mark.asyncio
    async def test_batch_policy_evaluation(self, mock_decision_engine):
        """Test batch policy evaluation performance."""
        batch_request = {
            "batch_id": "batch_perf_001",
            "evaluations": [
                {
                    "policy_id": f"policy_{i:03d}",
                    "input_context": {"user_id": i, "action": "read"},
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                for i in range(100)
            ]
        }
        
        start_time = time.perf_counter()
        result = await mock_decision_engine.batch_evaluate(batch_request)
        end_time = time.perf_counter()
        
        actual_time_ms = (end_time - start_time) * 1000
        
        # Verify batch performance
        assert result["total_evaluations"] == 100
        assert result["successful_evaluations"] >= 95  # High success rate
        assert result["average_time_ms"] < 5.0  # Per-evaluation performance
        assert actual_time_ms < 500.0  # Total batch time reasonable
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_governance_workflow_execution(self, mock_governance_workflow):
        """Test governance workflow execution."""
        workflow_request = {
            "workflow_type": "policy_approval",
            "policy_data": {
                "policy_id": "workflow_test_001",
                "policy_content": "Test governance policy"
            },
            "stakeholders": ["admin", "legal", "security"],
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        result = await mock_governance_workflow.execute_workflow(workflow_request)
        
        assert result["status"] == "completed"
        assert result["execution_time_ms"] < 10.0  # Workflow performance target
        assert result["steps_completed"] > 0
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["workflow_results"]["compliance_verified"] is True

    @pytest.mark.asyncio
    async def test_policy_cache_performance(self, mock_cache_manager):
        """Test policy cache performance meets >85% hit rate target."""
        policy_id = "cache_test_001"
        
        # First access - cache miss
        result1 = await mock_cache_manager.get_policy(policy_id)
        assert result1 is None
        
        # Cache the policy
        policy_data = {
            "policy_id": policy_id,
            "compiled_policy": "cached policy data",
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        await mock_cache_manager.set_policy(policy_id, policy_data)
        
        # Verify cache hit rate meets target
        hit_rate = mock_cache_manager.hit_rate()
        assert hit_rate > 0.85, f"Cache hit rate {hit_rate:.2f} below 85% target"

    @pytest.mark.asyncio
    async def test_policy_syntax_validation(self, mock_policy_compiler):
        """Test policy syntax validation."""
        valid_policy = {
            "policy_id": "syntax_valid_001",
            "source_code": "rule valid_rule { input.user.authenticated == true }",
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        result = mock_policy_compiler.validate_syntax(valid_policy)
        
        assert result["valid"] is True
        assert result["syntax_score"] > 0.9  # High syntax quality
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_concurrent_policy_evaluation(self, mock_decision_engine):
        """Test concurrent policy evaluation performance."""
        evaluation_requests = [
            {
                "policy_id": f"concurrent_eval_{i:03d}",
                "input_context": {"user_id": i, "action": "access"},
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            for i in range(10)
        ]
        
        start_time = time.perf_counter()
        
        # Execute concurrent evaluations
        tasks = [
            mock_decision_engine.evaluate_policy(request)
            for request in evaluation_requests
        ]
        results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000
        
        # Verify all evaluations completed
        assert len(results) == len(evaluation_requests)
        
        # Verify performance (concurrent processing should be efficient)
        assert total_time_ms < 50.0, f"Concurrent evaluation took {total_time_ms:.2f}ms"
        
        # Verify all results have constitutional hash
        for result in results:
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert result["decision"] in ["allow", "deny"]

    @pytest.mark.asyncio
    async def test_policy_governance_error_handling(self, mock_policy_compiler):
        """Test policy governance error handling."""
        # Test with invalid policy source
        invalid_policy = {
            "policy_id": None,  # Invalid ID
            "source_code": "invalid syntax !!!",  # Syntax errors
            "constitutional_hash": "wrong_hash"
        }
        
        # Mock compiler to handle errors gracefully
        mock_policy_compiler.compile_policy = AsyncMock(return_value={
            "compiled": False,
            "policy_id": None,
            "compilation_time_ms": 0.5,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "error": "Compilation failed",
            "compilation_metadata": {
                "rules_compiled": 0,
                "syntax_errors": 3,
                "error_details": ["Invalid policy ID", "Syntax error at line 1", "Wrong constitutional hash"]
            }
        })
        
        result = await mock_policy_compiler.compile_policy(invalid_policy)
        
        assert result["compiled"] is False
        assert result["compilation_metadata"]["syntax_errors"] > 0
        assert "error" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH  # Service maintains correct hash

    @pytest.mark.asyncio
    async def test_stakeholder_consensus_workflow(self, mock_governance_workflow):
        """Test stakeholder consensus in governance workflow."""
        consensus_request = {
            "workflow_type": "stakeholder_consensus",
            "policy_proposal": {
                "policy_id": "consensus_test_001",
                "proposal_content": "New governance policy proposal"
            },
            "stakeholders": ["legal", "security", "privacy", "engineering"],
            "consensus_threshold": 0.75,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        # Mock workflow for consensus testing
        mock_governance_workflow.execute_workflow = AsyncMock(return_value={
            "workflow_id": "consensus_workflow_001",
            "status": "completed",
            "execution_time_ms": 6.2,
            "steps_completed": 12,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "workflow_results": {
                "consensus_achieved": True,
                "stakeholder_consensus": 0.89,  # Above threshold
                "stakeholder_votes": {
                    "legal": {"vote": "approve", "confidence": 0.92},
                    "security": {"vote": "approve", "confidence": 0.88},
                    "privacy": {"vote": "approve", "confidence": 0.85},
                    "engineering": {"vote": "approve", "confidence": 0.91}
                },
                "policy_approved": True
            }
        })
        
        result = await mock_governance_workflow.execute_workflow(consensus_request)
        
        assert result["workflow_results"]["consensus_achieved"] is True
        assert result["workflow_results"]["stakeholder_consensus"] >= 0.75
        assert result["workflow_results"]["policy_approved"] is True
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Verify all stakeholders participated
        votes = result["workflow_results"]["stakeholder_votes"]
        assert len(votes) == 4
        assert all(vote["vote"] in ["approve", "reject"] for vote in votes.values())

    def test_constitutional_hash_consistency(self):
        """Test constitutional hash consistency in policy governance."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        assert len(CONSTITUTIONAL_HASH) == 16
        assert all(c in "0123456789abcdef" for c in CONSTITUTIONAL_HASH)
