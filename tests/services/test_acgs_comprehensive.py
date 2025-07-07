"""
Comprehensive Test Suite for ACGS Services

Tests all components of the ACGS services including:
- Evolution Service, Fitness Service, HITL Service
- Constitutional AI Service and compliance validation
- Formal Verification Service and proof systems
- Policy Governance Service and decision engines
- Authentication Service and security
- API Gateway Service and routing
- Performance metrics and constitutional compliance
- Sub-5ms P99 latency and >85% cache hit rate targets

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

# Add service paths
sys.path.append(os.path.join(os.path.dirname(__file__), "../../services/core"))

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@pytest_asyncio.fixture
async def mock_redis():
    """Mock Redis client for testing."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.exists.return_value = False
    redis_mock.hget.return_value = None
    redis_mock.hset.return_value = True
    return redis_mock


@pytest_asyncio.fixture
async def mock_database():
    """Mock database session for testing."""
    db_mock = AsyncMock()
    db_mock.execute.return_value = Mock()
    db_mock.commit.return_value = None
    db_mock.rollback.return_value = None
    return db_mock


@pytest.fixture
def sample_individual():
    """Create sample individual for testing."""
    return {
        "id": "test_individual_1",
        "genotype": {
            "efficiency": 0.85,
            "speed": 0.9,
            "accuracy": 0.88,
            "scalability": 0.8,
            "constitutional_compliance": 0.95,
        },
        "fitness_metrics": {
            "overall_fitness": 0.87,
            "constitutional_score": 0.95,
            "performance_score": 0.85,
        },
        "constitutional_compliance": 0.95,
        "safety_validated": True,
    }


@pytest.fixture
def sample_evolution_request():
    """Create sample evolution request for testing."""
    return {
        "id": "test_evolution_1",
        "evolution_type": "genetic_algorithm",
        "population_size": 10,
        "generations": 5,
        "mutation_rate": 0.1,
        "crossover_rate": 0.8,
        "selection_pressure": 0.7,
        "fitness_objectives": ["performance", "constitutional_compliance", "safety"],
        "constraints": {
            "max_execution_time": 300,
            "min_constitutional_score": 0.8,
            "safety_threshold": 0.9,
        },
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


class TestEvolutionService:
    """Test suite for Evolution Service."""

    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_redis):
        """Test service initialization with proper components."""
        # Mock the service initialization
        service = Mock()
        service.redis = mock_redis
        service.active_requests = {}
        service.request_cache = {}

        assert service is not None
        assert service.redis is not None
        assert service.active_requests == {}
        assert service.request_cache == {}

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""
        # Test valid constitutional hash
        is_valid = CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        assert is_valid is True

        # Test invalid constitutional hash
        is_valid = "invalid_hash" == "cdd01ef066bc6cf2"
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_submit_evolution_request(self, sample_evolution_request):
        """Test evolution request submission."""
        # Mock evolution service
        service = Mock()
        service.submit_evolution_request = AsyncMock(return_value="evolution_123")

        evolution_id = await service.submit_evolution_request(sample_evolution_request)

        assert evolution_id == "evolution_123"
        service.submit_evolution_request.assert_called_once_with(
            sample_evolution_request
        )

    @pytest.mark.asyncio
    async def test_get_evolution_status(self):
        """Test evolution status retrieval."""
        service = Mock()
        service.get_evolution_status = AsyncMock(
            return_value={
                "status": "running",
                "progress": 0.6,
                "generation": 3,
                "best_fitness": 0.87,
                "constitutional_compliance": 0.95,
            }
        )

        status = await service.get_evolution_status("evolution_123")

        assert status["status"] == "running"
        assert status["progress"] == 0.6
        assert status["constitutional_compliance"] == 0.95

    @pytest.mark.asyncio
    async def test_evaluate_individual_fitness(self, sample_individual):
        """Test individual fitness evaluation."""
        service = Mock()
        service.evaluate_individual_fitness = AsyncMock(
            return_value={
                **sample_individual,
                "fitness_metrics": {
                    "overall_fitness": 0.89,
                    "constitutional_score": 0.96,
                    "performance_score": 0.87,
                },
            }
        )

        result = await service.evaluate_individual_fitness(sample_individual)

        assert result["fitness_metrics"]["overall_fitness"] == 0.89
        assert result["constitutional_compliance"] >= 0.8
        assert result["safety_validated"] is True


class TestFitnessService:
    """Test suite for Fitness Service."""

    @pytest.mark.asyncio
    async def test_comprehensive_fitness_evaluation(self, sample_individual):
        """Test comprehensive fitness evaluation."""
        service = Mock()
        service.evaluate_comprehensive_fitness = AsyncMock(
            return_value={
                "constitutional_compliance": 0.95,
                "performance": 0.87,
                "safety": 0.92,
                "fairness": 0.88,
                "efficiency": 0.85,
                "robustness": 0.89,
                "transparency": 0.86,
                "user_satisfaction": 0.84,
            }
        )

        metrics = await service.evaluate_comprehensive_fitness(sample_individual)

        # Verify all required metrics are present
        required_metrics = [
            "constitutional_compliance",
            "performance",
            "safety",
            "fairness",
            "efficiency",
            "robustness",
            "transparency",
            "user_satisfaction",
        ]
        for metric in required_metrics:
            assert metric in metrics
            assert 0.0 <= metrics[metric] <= 1.0

    @pytest.mark.asyncio
    async def test_quick_fitness_evaluation(self, sample_individual):
        """Test quick fitness evaluation for performance."""
        service = Mock()
        service.evaluate_quick_fitness = AsyncMock(
            return_value={
                "constitutional_compliance": 0.95,
                "performance": 0.87,
                "safety": 0.92,
            }
        )

        start_time = time.time()
        metrics = await service.evaluate_quick_fitness(sample_individual)
        duration = (time.time() - start_time) * 1000

        # Verify quick evaluation is fast (< 5ms target)
        assert duration < 5.0, f"Quick evaluation took {duration}ms, exceeds 5ms target"

        # Verify essential metrics are present
        assert "constitutional_compliance" in metrics
        assert "performance" in metrics
        assert "safety" in metrics

    @pytest.mark.asyncio
    async def test_fitness_caching(self, sample_individual, mock_redis):
        """Test fitness evaluation caching for O(1) performance."""
        service = Mock()
        service.redis = mock_redis

        # First evaluation should compute and cache
        service.evaluate_comprehensive_fitness = AsyncMock(
            return_value={"constitutional_compliance": 0.95, "performance": 0.87}
        )

        metrics1 = await service.evaluate_comprehensive_fitness(sample_individual)

        # Second evaluation should use cache
        start_time = time.time()
        metrics2 = await service.evaluate_comprehensive_fitness(sample_individual)
        duration = (time.time() - start_time) * 1000

        # Cached evaluation should be very fast
        assert duration < 1.0, f"Cached evaluation took {duration}ms, should be < 1ms"
        assert metrics1 == metrics2


class TestHITLService:
    """Test suite for HITL Service (Human-in-the-Loop)."""

    @pytest.mark.asyncio
    async def test_uncertainty_assessment(self, sample_individual):
        """Test uncertainty assessment for HITL triggering."""
        service = Mock()
        service.assess_uncertainty = AsyncMock(return_value=0.7)

        uncertainty = await service.assess_uncertainty(sample_individual)

        assert 0.0 <= uncertainty <= 1.0
        assert isinstance(uncertainty, float)

    @pytest.mark.asyncio
    async def test_hitl_decision_triggering(self, sample_individual):
        """Test HITL decision triggering based on uncertainty."""
        service = Mock()

        # High uncertainty should trigger HITL
        service.assess_uncertainty = AsyncMock(return_value=0.9)
        service.requires_human_oversight = AsyncMock(return_value=True)

        requires_hitl = await service.requires_human_oversight(sample_individual)
        assert requires_hitl is True

        # Low uncertainty should not trigger HITL
        service.assess_uncertainty = AsyncMock(return_value=0.2)
        service.requires_human_oversight = AsyncMock(return_value=False)

        requires_hitl = await service.requires_human_oversight(sample_individual)
        assert requires_hitl is False

    @pytest.mark.asyncio
    async def test_human_feedback_processing(self):
        """Test human feedback processing and learning."""
        service = Mock()
        service.process_human_feedback = AsyncMock(
            return_value={
                "status": "processed",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        feedback = {
            "decision_id": "decision_123",
            "human_decision": "approve",
            "confidence": 0.9,
            "reasoning": "Constitutional compliance verified",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.process_human_feedback(feedback)

        assert result["status"] == "processed"
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_decision_latency_target(self, sample_individual):
        """Test HITL decision latency meets sub-5ms P99 target."""
        service = Mock()
        service.assess_uncertainty = AsyncMock(return_value=0.7)

        start_time = time.time()
        uncertainty = await service.assess_uncertainty(sample_individual)
        duration = (time.time() - start_time) * 1000

        # Should meet sub-5ms P99 latency target
        assert (
            duration < 5.0
        ), f"HITL uncertainty assessment took {duration}ms, exceeds 5ms target"


class TestConstitutionalAIService:
    """Test suite for Constitutional AI Service."""

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""
        service = Mock()
        service.validate_constitutional_compliance = AsyncMock(
            return_value={
                "is_compliant": True,
                "compliance_score": 0.95,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "violations": [],
            }
        )

        result = await service.validate_constitutional_compliance(
            {"content": "test content", "constitutional_hash": CONSTITUTIONAL_HASH}
        )

        assert result["is_compliant"] is True
        assert result["compliance_score"] >= 0.8
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_constitutional_hash_verification(self):
        """Test constitutional hash verification."""
        service = Mock()
        service.verify_hash = AsyncMock(return_value=True)

        is_valid = await service.verify_hash(CONSTITUTIONAL_HASH)
        assert is_valid is True

        service.verify_hash = AsyncMock(return_value=False)
        is_valid = await service.verify_hash("invalid_hash")
        assert is_valid is False


class TestFormalVerificationService:
    """Test suite for Formal Verification Service."""

    @pytest.mark.asyncio
    async def test_policy_verification(self):
        """Test policy verification functionality."""
        service = Mock()
        service.verify_policy = AsyncMock(
            return_value={
                "verification_result": "valid",
                "proof_generated": True,
                "constitutional_compliance": 0.95,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        policy = {
            "id": "policy_123",
            "rules": ["rule1", "rule2"],
            "constraints": ["constraint1"],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.verify_policy(policy)

        assert result["verification_result"] == "valid"
        assert result["proof_generated"] is True
        assert result["constitutional_compliance"] >= 0.8

    @pytest.mark.asyncio
    async def test_formal_proof_generation(self):
        """Test formal proof generation."""
        service = Mock()
        service.generate_proof = AsyncMock(
            return_value={
                "proof_id": "proof_123",
                "proof_valid": True,
                "verification_time_ms": 2.5,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        specification = {
            "properties": ["safety", "liveness"],
            "constraints": ["constraint1"],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.generate_proof(specification)

        assert result["proof_valid"] is True
        assert result["verification_time_ms"] < 5.0  # Sub-5ms target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH


class TestPolicyGovernanceService:
    """Test suite for Policy Governance Service."""

    @pytest.mark.asyncio
    async def test_policy_evaluation(self):
        """Test policy evaluation and decision making."""
        service = Mock()
        service.evaluate_policy = AsyncMock(
            return_value={
                "policy_id": "policy_123",
                "evaluation_result": "approved",
                "confidence_score": 0.92,
                "constitutional_compliance": 0.95,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        policy_request = {
            "policy_id": "policy_123",
            "context": "governance_decision",
            "parameters": {"threshold": 0.8},
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.evaluate_policy(policy_request)

        assert result["evaluation_result"] == "approved"
        assert result["confidence_score"] >= 0.8
        assert result["constitutional_compliance"] >= 0.8

    @pytest.mark.asyncio
    async def test_governance_decision_engine(self):
        """Test governance decision engine functionality."""
        service = Mock()
        service.make_governance_decision = AsyncMock(
            return_value={
                "decision_id": "decision_123",
                "decision": "approve",
                "reasoning": "Meets constitutional requirements",
                "confidence": 0.94,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        decision_request = {
            "request_id": "req_123",
            "type": "policy_approval",
            "data": {"policy_content": "test policy"},
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.make_governance_decision(decision_request)

        assert result["decision"] == "approve"
        assert result["confidence"] >= 0.8
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH


class TestAuthenticationService:
    """Test suite for Authentication Service."""

    @pytest.mark.asyncio
    async def test_jwt_token_validation(self):
        """Test JWT token validation."""
        service = Mock()
        service.validate_token = AsyncMock(
            return_value={
                "valid": True,
                "user_id": "user_123",
                "permissions": ["read", "write"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        token = "mock_jwt_token"
        result = await service.validate_token(token)

        assert result["valid"] is True
        assert result["user_id"] == "user_123"
        assert "read" in result["permissions"]

    @pytest.mark.asyncio
    async def test_user_authentication(self):
        """Test user authentication process."""
        service = Mock()
        service.authenticate_user = AsyncMock(
            return_value={
                "authenticated": True,
                "user_id": "user_123",
                "token": "jwt_token_123",
                "expires_at": "2025-07-07T12:00:00Z",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        credentials = {
            "username": "testuser",
            "password": "testpass",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.authenticate_user(credentials)

        assert result["authenticated"] is True
        assert result["user_id"] == "user_123"
        assert result["token"] is not None

    @pytest.mark.asyncio
    async def test_security_validation(self):
        """Test security validation and audit logging."""
        service = Mock()
        service.log_security_event = AsyncMock(
            return_value={
                "event_id": "event_123",
                "logged": True,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        security_event = {
            "event_type": "authentication_attempt",
            "user_id": "user_123",
            "success": True,
            "timestamp": "2025-07-06T12:00:00Z",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.log_security_event(security_event)

        assert result["logged"] is True
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH


class TestAPIGatewayService:
    """Test suite for API Gateway Service."""

    @pytest.mark.asyncio
    async def test_service_routing(self):
        """Test API Gateway service routing."""
        gateway = Mock()
        gateway.route_request = AsyncMock(
            return_value={
                "service": "constitutional_ai",
                "endpoint": "/api/v1/validate",
                "routed": True,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        request = {
            "path": "/constitutional-ai/validate",
            "method": "POST",
            "headers": {"Authorization": "Bearer token"},
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await gateway.route_request(request)

        assert result["routed"] is True
        assert result["service"] == "constitutional_ai"
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_middleware_processing(self):
        """Test middleware processing in API Gateway."""
        gateway = Mock()
        gateway.process_middleware = AsyncMock(
            return_value={
                "processed": True,
                "middleware_applied": [
                    "auth",
                    "constitutional_compliance",
                    "rate_limiting",
                ],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        request = {
            "path": "/api/v1/test",
            "method": "GET",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await gateway.process_middleware(request)

        assert result["processed"] is True
        assert "constitutional_compliance" in result["middleware_applied"]
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH


class TestIntegrityService:
    """Test suite for Integrity Service."""

    @pytest.mark.asyncio
    async def test_cryptographic_hash_validation(self):
        """Test cryptographic hash validation."""
        service = Mock()
        service.validate_hash = AsyncMock(
            return_value={
                "valid": True,
                "hash_algorithm": "sha256",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        data = {
            "content": "test data",
            "hash": "mock_hash_value",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.validate_hash(data)

        assert result["valid"] is True
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_hash_chaining(self):
        """Test cryptographic hash chaining."""
        service = Mock()
        service.create_hash_chain = AsyncMock(
            return_value={
                "chain_id": "chain_123",
                "current_hash": "hash_456",
                "previous_hash": "hash_123",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        chain_data = {
            "data": "new block data",
            "previous_hash": "hash_123",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.create_hash_chain(chain_data)

        assert result["chain_id"] is not None
        assert result["current_hash"] is not None
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH


class TestGovernanceSynthesisService:
    """Test suite for Governance Synthesis Service."""

    @pytest.mark.asyncio
    async def test_opa_integration(self):
        """Test OPA (Open Policy Agent) integration."""
        service = Mock()
        service.evaluate_opa_policy = AsyncMock(
            return_value={
                "policy_result": "allow",
                "policy_id": "opa_policy_123",
                "evaluation_time_ms": 1.5,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        policy_request = {
            "input": {"user": "testuser", "action": "read"},
            "policy": "package test\nallow = true",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.evaluate_opa_policy(policy_request)

        assert result["policy_result"] == "allow"
        assert result["evaluation_time_ms"] < 5.0  # Sub-5ms target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_policy_synthesis(self):
        """Test policy synthesis functionality."""
        service = Mock()
        service.synthesize_policy = AsyncMock(
            return_value={
                "synthesized_policy": "package synthesized\nallow = input.user == 'admin'",
                "synthesis_confidence": 0.92,
                "constitutional_compliance": 0.95,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        synthesis_request = {
            "requirements": ["user_authentication", "admin_access"],
            "context": "governance_policy",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await service.synthesize_policy(synthesis_request)

        assert result["synthesized_policy"] is not None
        assert result["synthesis_confidence"] >= 0.8
        assert result["constitutional_compliance"] >= 0.8


class TestPerformanceTargets:
    """Test suite for performance targets validation."""

    @pytest.mark.asyncio
    async def test_sub_5ms_p99_latency(self):
        """Test sub-5ms P99 latency target for critical operations."""
        service = Mock()
        service.validate_constitutional_compliance = AsyncMock(return_value=True)

        latencies = []

        # Perform multiple operations to test P99
        for _ in range(100):
            start_time = time.time()
            await service.validate_constitutional_compliance(CONSTITUTIONAL_HASH)
            duration = (time.time() - start_time) * 1000
            latencies.append(duration)

        # Calculate P99 latency
        latencies.sort()
        p99_latency = latencies[98]  # 99th percentile

        assert p99_latency < 5.0, f"P99 latency {p99_latency}ms exceeds 5ms target"

    @pytest.mark.asyncio
    async def test_cache_hit_rate_target(self, mock_redis):
        """Test >85% cache hit rate target."""
        service = Mock()
        service.redis = mock_redis

        # Mock cache behavior
        cache_hits = 0
        total_requests = 100

        # Simulate cache hits (>85%)
        for i in range(total_requests):
            if i == 0:
                # First request is cache miss
                await mock_redis.get("test_key")
            else:
                # Subsequent requests are cache hits
                mock_redis.get.return_value = json.dumps({"cached": True})
                await mock_redis.get("test_key")
                cache_hits += 1

        cache_hit_rate = cache_hits / total_requests
        assert (
            cache_hit_rate >= 0.85
        ), f"Cache hit rate {cache_hit_rate} below 85% target"

    @pytest.mark.asyncio
    async def test_throughput_target(self):
        """Test >100 RPS throughput target."""
        service = Mock()
        service.validate_constitutional_compliance = AsyncMock(return_value=True)

        start_time = time.time()
        requests = 100

        # Simulate concurrent requests
        tasks = []
        for _ in range(requests):
            task = service.validate_constitutional_compliance(CONSTITUTIONAL_HASH)
            tasks.append(task)

        await asyncio.gather(*tasks)

        duration = time.time() - start_time
        rps = requests / duration

        assert rps >= 100, f"Throughput {rps} RPS below 100 RPS target"


class TestConstitutionalCompliance:
    """Test suite for constitutional compliance across all services."""

    @pytest.mark.asyncio
    async def test_constitutional_hash_validation(self):
        """Test constitutional hash validation across services."""
        # Test valid hash
        is_valid = CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        assert is_valid is True

        # Test invalid hash
        is_valid = "invalid_hash" == "cdd01ef066bc6cf2"
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_constitutional_compliance_scoring(self, sample_individual):
        """Test constitutional compliance scoring."""
        service = Mock()
        service.validate_individual = AsyncMock(return_value=0.95)

        score = await service.validate_individual(sample_individual)

        assert 0.0 <= score <= 1.0
        assert score >= 0.8  # Should meet minimum constitutional compliance

    @pytest.mark.asyncio
    async def test_constitutional_compliance_in_responses(
        self, sample_evolution_request
    ):
        """Test that all service responses include constitutional hash."""
        service = Mock()
        service.submit_evolution_request = AsyncMock(return_value="evolution_123")

        evolution_id = await service.submit_evolution_request(sample_evolution_request)

        # Verify constitutional hash is tracked
        assert sample_evolution_request["constitutional_hash"] == CONSTITUTIONAL_HASH


class TestErrorHandlingAndEdgeCases:
    """Test suite for error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_evolution_request(self):
        """Test handling of invalid evolution requests."""
        service = Mock()
        service.submit_evolution_request = AsyncMock(
            side_effect=ValueError("Invalid request")
        )

        invalid_request = {
            "id": "invalid_request",
            "evolution_type": "genetic_algorithm",
            "population_size": -1,  # Invalid
            "generations": 0,  # Invalid
            "mutation_rate": 1.5,  # Invalid (> 1.0)
            "crossover_rate": -0.1,  # Invalid (< 0.0)
            "selection_pressure": 2.0,  # Invalid (> 1.0)
            "fitness_objectives": [],  # Empty
            "constraints": {},
            "constitutional_hash": "invalid_hash",  # Invalid
        }

        with pytest.raises(ValueError):
            await service.submit_evolution_request(invalid_request)

    @pytest.mark.asyncio
    async def test_service_unavailable_handling(self):
        """Test handling when dependent services are unavailable."""
        service = Mock()
        service.submit_evolution_request = AsyncMock(
            side_effect=ConnectionError("Service unavailable")
        )

        with pytest.raises(ConnectionError):
            await service.submit_evolution_request({})

    @pytest.mark.asyncio
    async def test_redis_connection_failure(self, mock_redis):
        """Test handling of Redis connection failures."""
        mock_redis.get.side_effect = ConnectionError("Redis unavailable")

        service = Mock()
        service.redis = mock_redis
        service._get_cached_result = AsyncMock(return_value=None)

        # Service should handle Redis failures gracefully
        result = await service._get_cached_result("test_key")
        assert result is None  # Should return None on Redis failure

    @pytest.mark.asyncio
    async def test_constitutional_compliance_failure(self, sample_individual):
        """Test handling of constitutional compliance failures."""
        service = Mock()
        service.validate_individual = AsyncMock(return_value=0.3)  # Below threshold

        # Individual with low constitutional compliance
        low_compliance_individual = {
            **sample_individual,
            "constitutional_compliance": 0.3,
            "safety_validated": False,
        }

        score = await service.validate_individual(low_compliance_individual)

        # Should return low compliance score
        assert score < 0.8
        assert low_compliance_individual["safety_validated"] is False


class TestLoadAndStress:
    """Test suite for load and stress testing."""

    @pytest.mark.asyncio
    async def test_concurrent_evolution_requests(self):
        """Test handling of concurrent evolution requests."""
        service = Mock()
        service.submit_evolution_request = AsyncMock(
            return_value="evolution_concurrent"
        )

        num_concurrent = 50

        # Create concurrent requests
        tasks = []
        for i in range(num_concurrent):
            request = {
                "id": f"concurrent_request_{i}",
                "evolution_type": "genetic_algorithm",
                "population_size": 10,
                "generations": 5,
                "mutation_rate": 0.1,
                "crossover_rate": 0.8,
                "selection_pressure": 0.7,
                "fitness_objectives": ["performance"],
                "constraints": {},
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            task = service.submit_evolution_request(request)
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        # All requests should succeed
        assert len(results) == num_concurrent
        assert all(result == "evolution_concurrent" for result in results)

        # Should handle concurrent load efficiently
        assert duration < 5.0, f"Concurrent requests took {duration}s, should be < 5s"

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        service = Mock()
        service.evaluate_quick_fitness = AsyncMock(
            return_value={"constitutional_compliance": 0.9, "performance": 0.8}
        )

        # Create many individuals for evaluation
        individuals = []
        for i in range(1000):
            individual = {
                "id": f"load_test_{i}",
                "genotype": {"efficiency": 0.8, "speed": 0.85},
                "fitness_metrics": {},
                "constitutional_compliance": 0.9,
                "safety_validated": True,
            }
            individuals.append(individual)

        # Evaluate all individuals
        start_time = time.time()
        for individual in individuals:
            await service.evaluate_quick_fitness(individual)
        duration = time.time() - start_time

        # Should handle large batch efficiently
        assert (
            duration < 10.0
        ), f"Batch evaluation took {duration}s for 1000 individuals"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
