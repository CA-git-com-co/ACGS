"""
Unit Tests for Generation Engine

Tests for policy generation, constitutional compliance, and quantum-inspired enhancements.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from services.core.generation_engine.engine import (
    GenerationConfig,
    GenerationEngine,
    PolicyGenerationRequest,
)
from services.core.generation_engine.models import (
    LSU,
    Representation,
    RepresentationSet,
    RepresentationType,
)


@pytest.mark.unit
class TestGenerationEngine:
    """Test suite for Generation Engine functionality."""

    @pytest_asyncio.fixture
    async def generation_config(self, test_config):
        """Create generation config for testing."""
        return GenerationConfig(
            gs_service_url=test_config["gs_service_url"],
            pgc_service_url=test_config["pgc_service_url"],
            constitutional_hash=test_config["constitutional_hash"],
        )

    @pytest_asyncio.fixture
    async def generation_engine(self, generation_config):
        """Create generation engine for testing."""
        return GenerationEngine(generation_config)

    async def test_generation_engine_initialization(self, generation_engine, generation_config):
        """Test generation engine initialization."""
        assert generation_engine.config == generation_config
        assert generation_engine.constitutional_hash == "cdd01ef066bc6cf2"
        assert generation_engine.http_client is not None

    async def test_health_check(self, generation_engine):
        """Test generation engine health check."""
        health_status = await generation_engine.health_check()

        assert "status" in health_status
        assert "constitutional_hash" in health_status
        assert health_status["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert "timestamp" in health_status

    async def test_get_metrics(self, generation_engine):
        """Test generation engine metrics retrieval."""
        metrics = await generation_engine.get_metrics()

        assert "status" in metrics
        assert "constitutional_hash" in metrics
        assert "performance" in metrics
        assert "generation_statistics" in metrics

    @patch("src.generation_engine.engine.httpx.AsyncClient")
    async def test_policy_generation_success(
        self, mock_client, generation_engine, sample_policy_request
    ):
        """Test successful policy generation."""
        # Mock HTTP responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "compliance_score": 0.85,
            "validation_result": "compliant",
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Create request
        request = PolicyGenerationRequest(**sample_policy_request)

        # Generate policy
        response = await generation_engine.generate_policy(request, use_quantum_enhancement=True)

        # Verify response
        assert response.generation_id is not None
        assert response.policy_content is not None
        assert response.constitutional_compliance_score >= 0.8
        assert response.confidence_score > 0.0
        assert response.constitutional_hash == "cdd01ef066bc6cf2"
        assert response.generation_time_ms > 0

    async def test_policy_generation_performance(
        self, generation_engine, sample_policy_request, test_metrics
    ):
        """Test policy generation performance targets."""
        request = PolicyGenerationRequest(**sample_policy_request)

        start_time = datetime.now()

        with patch("src.generation_engine.engine.httpx.AsyncClient") as mock_client:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "compliance_score": 0.85,
                "validation_result": "compliant",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            response = await generation_engine.generate_policy(request)

        end_time = datetime.now()
        response_time_ms = (end_time - start_time).total_seconds() * 1000

        # Record metrics
        test_metrics.record_response_time(response_time_ms)
        test_metrics.record_compliance_score(response.constitutional_compliance_score)

        # Verify performance targets
        assert response_time_ms <= 500.0  # <500ms target
        assert response.constitutional_compliance_score >= 0.8  # >80% compliance

    async def test_constitutional_compliance_validation(self, generation_engine):
        """Test constitutional compliance validation."""
        test_content = "Test policy content for constitutional validation"

        with patch("src.generation_engine.engine.httpx.AsyncClient") as mock_client:
            # Mock PGC service response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "compliance_score": 0.92,
                "validation_result": "compliant",
                "constitutional_hash": "cdd01ef066bc6cf2",
                "violations": [],
            }

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            compliance_result = await generation_engine._validate_constitutional_compliance(
                test_content
            )

        assert compliance_result["compliance_score"] >= 0.8
        assert compliance_result["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert compliance_result["validation_result"] == "compliant"

    async def test_service_connectivity_check(self, generation_engine):
        """Test service connectivity checks."""
        with patch("src.generation_engine.engine.httpx.AsyncClient") as mock_client:
            # Mock successful health check
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            gs_healthy = await generation_engine._check_gs_service_health()
            pgc_healthy = await generation_engine._check_pgc_service_health()

        assert gs_healthy is True
        assert pgc_healthy is True

    async def test_error_handling(self, generation_engine, sample_policy_request):
        """Test error handling in policy generation."""
        request = PolicyGenerationRequest(**sample_policy_request)

        with patch("src.generation_engine.engine.httpx.AsyncClient") as mock_client:
            # Mock service failure
            mock_client_instance = AsyncMock()
            mock_client_instance.post.side_effect = Exception("Service unavailable")
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            with pytest.raises(Exception):
                await generation_engine.generate_policy(request)

    async def test_cleanup(self, generation_engine):
        """Test generation engine cleanup."""
        await generation_engine.close()
        # Verify cleanup completed without errors


@pytest.mark.unit
class TestGenerationModels:
    """Test suite for Generation Engine models."""

    def test_lsu_creation(self):
        """Test LSU (Logical Semantic Unit) creation."""
        content = "Test policy content"
        lsu = LSU(content=content, representation_type=RepresentationType.POLICY_DRAFT)

        assert lsu.content == content
        assert lsu.representation_type == RepresentationType.POLICY_DRAFT
        assert lsu.semantic_hash is not None
        assert len(lsu.error_correction_bits) > 0
        assert lsu.constitutional_compliance_score >= 0.0

    def test_lsu_error_correction(self):
        """Test LSU error correction capabilities."""
        content = "Test policy content"
        lsu = LSU(content=content, representation_type=RepresentationType.POLICY_DRAFT)

        # Test error detection
        errors_detected = lsu.detect_errors()
        assert isinstance(errors_detected, list)

        # Test error correction
        corrected_lsu = lsu.apply_error_correction()
        assert corrected_lsu.content is not None
        assert corrected_lsu.semantic_hash is not None

    def test_representation_creation(self):
        """Test Representation creation and validation."""
        lsu = LSU(content="Test content", representation_type=RepresentationType.POLICY_DRAFT)
        representation = Representation(
            lsu=lsu, confidence_score=0.85, constitutional_compliance_score=0.90
        )

        assert representation.lsu == lsu
        assert representation.confidence_score == 0.85
        assert representation.constitutional_compliance_score == 0.90
        assert representation.is_constitutionally_compliant() is True

    def test_representation_set_consensus(self):
        """Test RepresentationSet consensus mechanisms."""
        # Create multiple representations
        representations = []
        for i in range(3):
            lsu = LSU(
                content=f"Test content {i}",
                representation_type=RepresentationType.POLICY_DRAFT,
            )
            representation = Representation(
                lsu=lsu,
                confidence_score=0.8 + (i * 0.05),
                constitutional_compliance_score=0.85 + (i * 0.03),
            )
            representations.append(representation)

        rep_set = RepresentationSet(representations=representations)

        # Test consensus achievement
        consensus_rep = rep_set.achieve_consensus(threshold=0.7)
        assert consensus_rep is not None
        assert consensus_rep.confidence_score >= 0.7

        # Test semantic diversity
        diversity = rep_set.get_semantic_diversity()
        assert 0.0 <= diversity <= 1.0

    def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation in models."""
        lsu = LSU(
            content="Constitutional policy content",
            representation_type=RepresentationType.POLICY_DRAFT,
        )

        # Test compliance scoring
        assert 0.0 <= lsu.constitutional_compliance_score <= 1.0

        # Test compliance validation
        representation = Representation(
            lsu=lsu, confidence_score=0.85, constitutional_compliance_score=0.95
        )

        assert representation.is_constitutionally_compliant() is True

        # Test non-compliant case
        non_compliant_representation = Representation(
            lsu=lsu, confidence_score=0.85, constitutional_compliance_score=0.75
        )

        assert non_compliant_representation.is_constitutionally_compliant() is False
