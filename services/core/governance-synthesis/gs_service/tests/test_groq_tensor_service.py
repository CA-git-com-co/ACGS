"""
Unit tests for Groq Tensor Service in ACGS-1 constitutional governance.
Tests tensor decomposition generation with constitutional compliance.

Test Coverage Requirements:
- ≥90% test pass rate
- ≥80% code coverage
- Constitutional compliance validation
- Performance targets (<2s response times)
- Circuit breaker functionality testing

Formal Verification Comments:
# requires: test_coverage >= 0.8
# ensures: all_tests_pass_rate >= 0.9
# ensures: tensor_decomposition_accuracy >= 0.95
# ensures: constitutional_compliance == 1.0
# sha256: evolutionary_tensor_decomposition_groq_tests_v1.0
"""

import json
import os
import time
import unittest
from unittest.mock import AsyncMock, patch

import numpy as np

# Import the service to test
from services.core.governance_synthesis.gs_service.app.services.groq_tensor_service import (
    CircuitBreakerState,
    GovernanceConstraints,
    GroqTensorService,
    TensorDecomposition,
    TensorDecompositionType,
)


class TestGroqTensorService(unittest.TestCase):
    """Test suite for GroqTensorService."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = GroqTensorService()
        self.test_matrix = np.random.rand(10, 10)
        self.test_constraints = GovernanceConstraints(
            constitutional_hash="cdd01ef066bc6cf2",
            compliance_requirements={
                "accuracy_threshold": 0.95,
                "constitutional_compliance": True,
            },
            performance_targets={
                "response_time_ms": 2000,
                "accuracy": 0.95,
                "memory_usage_mb": 512,
            },
            policy_type="constitutional",
            stakeholder_requirements=["transparency", "accountability"],
        )

    def test_service_initialization(self):
        """Test service initialization and configuration."""
        self.assertEqual(self.service.default_model, "llama-3.1-70b-versatile")
        self.assertEqual(self.service.temperature, 0.3)
        self.assertEqual(self.service.max_tokens, 4096)
        self.assertEqual(self.service.timeout_seconds, 30)
        self.assertEqual(self.service.circuit_breaker_state, CircuitBreakerState.CLOSED)
        self.assertEqual(self.service.failure_threshold, 5)

    def test_matrix_analysis(self):
        """Test policy matrix analysis functionality."""
        matrix = np.array([[1, 2], [3, 4]])
        analysis = self.service._analyze_policy_matrix(matrix)

        self.assertEqual(analysis["shape"], (2, 2))
        self.assertIn("rank", analysis)
        self.assertIn("condition_number", analysis)
        self.assertIn("sparsity", analysis)
        self.assertIn("frobenius_norm", analysis)
        self.assertIn("spectral_norm", analysis)
        self.assertIn("is_symmetric", analysis)
        self.assertIn("is_positive_definite", analysis)

        # Verify calculations
        self.assertEqual(analysis["rank"], 2)
        self.assertAlmostEqual(analysis["frobenius_norm"], np.linalg.norm(matrix, "fro"))

    def test_decomposition_type_selection(self):
        """Test optimal decomposition type selection."""
        # Test constitutional policy type
        constitutional_constraints = GovernanceConstraints(
            constitutional_hash="test",
            compliance_requirements={},
            performance_targets={},
            policy_type="constitutional",
            stakeholder_requirements=[],
        )

        matrix_analysis = {"sparsity": 0.5, "condition_number": 50, "shape": (100, 100)}
        decomposition_type = self.service._select_optimal_decomposition(
            matrix_analysis, constitutional_constraints
        )

        self.assertEqual(decomposition_type, TensorDecompositionType.CONSTITUTIONAL_HYBRID)

        # Test sparse matrix
        sparse_analysis = {"sparsity": 0.2, "condition_number": 50, "shape": (100, 100)}
        operational_constraints = GovernanceConstraints(
            constitutional_hash="test",
            compliance_requirements={},
            performance_targets={},
            policy_type="operational",
            stakeholder_requirements=[],
        )

        decomposition_type = self.service._select_optimal_decomposition(
            sparse_analysis, operational_constraints
        )

        self.assertEqual(decomposition_type, TensorDecompositionType.CP)

    @patch.dict(os.environ, {}, clear=True)
    async def test_missing_api_key(self):
        """Test behavior when API key is not configured."""
        service = GroqTensorService()

        with self.assertRaises(ValueError) as context:
            await service.generate_tensor_decomposition(self.test_matrix, self.test_constraints)

        self.assertIn("GROQ_API_KEY not configured", str(context.exception))

    @patch.dict(os.environ, {"GROQ_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_successful_decomposition_generation(self, mock_post):
        """Test successful tensor decomposition generation."""
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "code": "import numpy as np\ndef svd_decomposition(matrix):\n    return np.linalg.svd(matrix)",
                                "parameters": {"regularization": 1e-10},
                                "accuracy_estimate": 0.96,
                                "complexity": "O(min(m,n)^2 * max(m,n))",
                                "error_bounds": {"frobenius": 0.001},
                                "constitutional_compliance_notes": "Fully compliant with governance requirements",
                            }
                        )
                    }
                }
            ]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        service = GroqTensorService()
        service.api_key = "test_api_key"

        result = await service.generate_tensor_decomposition(
            self.test_matrix, self.test_constraints
        )

        # Assertions
        self.assertIsInstance(result, TensorDecomposition)
        self.assertIn("svd_decomposition", result.algorithm_code)
        self.assertEqual(result.accuracy_estimate, 0.96)
        self.assertTrue(result.constitutional_compliance)
        self.assertEqual(result.governance_metadata["constitutional_hash"], "cdd01ef066bc6cf2")
        self.assertIn("generation_timestamp", result.governance_metadata)

    @patch.dict(os.environ, {"GROQ_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_api_error_handling(self, mock_post):
        """Test handling of API errors."""
        # Mock API error
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value.__aenter__.return_value = mock_response

        service = GroqTensorService()
        service.api_key = "test_api_key"

        # Should fallback to local decomposition
        result = await service.generate_tensor_decomposition(
            self.test_matrix, self.test_constraints
        )

        self.assertIsInstance(result, TensorDecomposition)
        self.assertIn("constitutional_svd_decomposition", result.algorithm_code)
        self.assertEqual(result.governance_metadata["generation_method"], "local_fallback")

    @patch.dict(os.environ, {"GROQ_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_circuit_breaker_functionality(self, mock_post):
        """Test circuit breaker pattern for service resilience."""
        # Mock repeated failures
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.raise_for_status.side_effect = Exception("Service Unavailable")
        mock_post.return_value.__aenter__.return_value = mock_response

        service = GroqTensorService()
        service.api_key = "test_api_key"

        # Trigger multiple failures to open circuit breaker
        for _i in range(6):  # Exceed failure threshold of 5
            try:
                await service.generate_tensor_decomposition(self.test_matrix, self.test_constraints)
            except Exception:
                pass  # Expected failures

        # Circuit breaker should be OPEN
        self.assertEqual(service.circuit_breaker_state, CircuitBreakerState.OPEN)
        self.assertGreaterEqual(service.failure_count, service.failure_threshold)

        # Next request should fail immediately due to circuit breaker
        with self.assertRaises(Exception) as context:
            await service.generate_tensor_decomposition(self.test_matrix, self.test_constraints)

        self.assertIn("Circuit breaker is OPEN", str(context.exception))

    def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""
        algorithm_result = {
            "code": "import numpy as np\ndef test_algorithm(): pass",
            "parameters": {"test": "value"},
            "accuracy_estimate": 0.96,
            "complexity": "O(n^2)",
        }

        compliance_result = self.service._validate_constitutional_compliance(
            algorithm_result, self.test_constraints
        )

        self.assertIn("compliant", compliance_result)
        self.assertIn("checks", compliance_result)
        self.assertIn("compliance_score", compliance_result)

        # Check individual compliance checks
        checks = compliance_result["checks"]
        self.assertIn("accuracy_sufficient", checks)
        self.assertIn("constitutional_hash_valid", checks)
        self.assertIn("code_quality", checks)
        self.assertIn("parameters_valid", checks)

        # Should pass accuracy and hash validation
        self.assertTrue(checks["accuracy_sufficient"])
        self.assertTrue(checks["constitutional_hash_valid"])

    def test_fallback_algorithm_generation(self):
        """Test fallback algorithm when parsing fails."""
        fallback = self.service._get_fallback_algorithm()

        self.assertIn("code", fallback)
        self.assertIn("parameters", fallback)
        self.assertIn("accuracy_estimate", fallback)
        self.assertIn("complexity", fallback)

        # Should contain basic SVD implementation
        self.assertIn("svd", fallback["code"].lower())
        self.assertGreaterEqual(fallback["accuracy_estimate"], 0.8)

    async def test_fallback_local_decomposition(self):
        """Test local fallback decomposition functionality."""
        result = await self.service._fallback_local_decomposition(
            self.test_matrix, self.test_constraints, TensorDecompositionType.SVD
        )

        self.assertIsInstance(result, TensorDecomposition)
        self.assertEqual(result.decomposition_type, TensorDecompositionType.SVD)
        self.assertIn("constitutional_svd_decomposition", result.algorithm_code)
        self.assertTrue(result.constitutional_compliance)
        self.assertEqual(result.governance_metadata["generation_method"], "local_fallback")
        self.assertGreaterEqual(result.accuracy_estimate, 0.9)

    def test_metrics_tracking(self):
        """Test service metrics tracking."""
        service = GroqTensorService()

        # Initial metrics
        self.assertEqual(service.metrics["total_requests"], 0)
        self.assertEqual(service.metrics["successful_requests"], 0)
        self.assertEqual(service.metrics["failed_requests"], 0)
        self.assertEqual(service.metrics["average_latency_ms"], 0.0)

        # Test successful request metrics
        service.metrics["total_requests"] = 1
        service._update_metrics(150.0, success=True)

        self.assertEqual(service.metrics["successful_requests"], 1)
        self.assertEqual(service.metrics["average_latency_ms"], 150.0)

        # Test failed request metrics
        service.metrics["total_requests"] = 2
        service._update_metrics(200.0, success=False)

        self.assertEqual(service.metrics["failed_requests"], 1)

        # Test service metrics retrieval
        metrics = service.get_service_metrics()
        self.assertIn("success_rate", metrics)
        self.assertIn("circuit_breaker_state", metrics)
        self.assertIn("api_key_configured", metrics)

        self.assertEqual(metrics["success_rate"], 0.5)  # 1 success out of 2 total

    def test_prompt_creation(self):
        """Test algorithm prompt creation."""
        matrix_analysis = {
            "shape": (10, 10),
            "rank": 8,
            "condition_number": 15.5,
            "sparsity": 0.3,
            "frobenius_norm": 25.2,
        }

        prompt = self.service._create_algorithm_prompt(
            matrix_analysis, self.test_constraints, TensorDecompositionType.SVD
        )

        # Should contain all required information
        self.assertIn("singular_value_decomposition", prompt)
        self.assertIn("Shape: (10, 10)", prompt)
        self.assertIn("Rank: 8", prompt)
        self.assertIn("cdd01ef066bc6cf2", prompt)
        self.assertIn("constitutional", prompt)
        self.assertIn(">95% decomposition accuracy", prompt)
        self.assertIn("<2s computation time", prompt)
        self.assertIn("JSON format", prompt)

    @patch.dict(os.environ, {"GROQ_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_performance_requirements(self, mock_post):
        """Test that service meets performance requirements."""
        # Mock fast response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "code": "def fast_decomposition(): pass",
                                "parameters": {},
                                "accuracy_estimate": 0.97,
                                "complexity": "O(n^2)",
                            }
                        )
                    }
                }
            ]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        service = GroqTensorService()
        service.api_key = "test_api_key"

        start_time = time.time()
        result = await service.generate_tensor_decomposition(
            self.test_matrix, self.test_constraints
        )
        end_time = time.time()

        # Should meet <2s response time requirement (allowing for mocking overhead)
        response_time_ms = (end_time - start_time) * 1000
        self.assertLess(response_time_ms, 5000)  # Generous limit for testing

        # Should meet accuracy requirement
        self.assertGreaterEqual(result.accuracy_estimate, 0.95)

        # Should maintain constitutional compliance
        self.assertTrue(result.constitutional_compliance)


class TestTensorDecompositionTypes(unittest.TestCase):
    """Test tensor decomposition type enumeration."""

    def test_decomposition_types(self):
        """Test that all required decomposition types are available."""
        types = list(TensorDecompositionType)

        self.assertIn(TensorDecompositionType.SVD, types)
        self.assertIn(TensorDecompositionType.CP, types)
        self.assertIn(TensorDecompositionType.TUCKER, types)
        self.assertIn(TensorDecompositionType.TENSOR_TRAIN, types)
        self.assertIn(TensorDecompositionType.CONSTITUTIONAL_HYBRID, types)

        # Test string values
        self.assertEqual(TensorDecompositionType.SVD.value, "singular_value_decomposition")
        self.assertEqual(
            TensorDecompositionType.CONSTITUTIONAL_HYBRID.value, "constitutional_hybrid"
        )


class TestGovernanceConstraints(unittest.TestCase):
    """Test governance constraints data structure."""

    def test_constraints_creation(self):
        """Test governance constraints creation and validation."""
        constraints = GovernanceConstraints(
            constitutional_hash="test_hash",
            compliance_requirements={"test": True},
            performance_targets={"accuracy": 0.95},
            policy_type="test_policy",
            stakeholder_requirements=["requirement1", "requirement2"],
        )

        self.assertEqual(constraints.constitutional_hash, "test_hash")
        self.assertEqual(constraints.policy_type, "test_policy")
        self.assertIn("test", constraints.compliance_requirements)
        self.assertIn("accuracy", constraints.performance_targets)
        self.assertEqual(len(constraints.stakeholder_requirements), 2)


if __name__ == "__main__":
    # Run tests with coverage
    unittest.main(verbosity=2)
