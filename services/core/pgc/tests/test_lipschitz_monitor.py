"""
Comprehensive unit tests for Lipschitz Constant Real-Time Monitoring
Target: >90% test coverage with stability validation

Tests cover:
- Lipschitz constant calculation
- Stability threshold monitoring
- Alert generation and management
- Trend analysis and forecasting
- Performance metrics tracking
- Recalibration mechanisms
"""

import asyncio
import os

# Import the module under test
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "monitoring"))

from lipschitz_monitor import (
    AlertSeverity,
    LipschitzMonitor,
    LipschitzSample,
    PolicyState,
    PrincipleState,
    StabilityAlert,
    StabilityLevel,
    get_lipschitz_monitor,
)


class TestStabilityLevel:
    """Test StabilityLevel enum."""

    def test_stability_level_values(self):
        """Test stability level enum values."""
        assert StabilityLevel.STABLE.value == "stable"
        assert StabilityLevel.MODERATE.value == "moderate"
        assert StabilityLevel.WARNING.value == "warning"
        assert StabilityLevel.CRITICAL.value == "critical"


class TestAlertSeverity:
    """Test AlertSeverity enum."""

    def test_alert_severity_values(self):
        """Test alert severity enum values."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestPolicyState:
    """Test PolicyState dataclass."""

    def test_policy_state_creation(self):
        """Test policy state creation."""
        embedding = np.array([0.1, 0.2, 0.3, 0.4])
        policy_state = PolicyState(
            policy_id="POL-001",
            content="Test policy content",
            embedding=embedding,
            version=2,
        )

        assert policy_state.policy_id == "POL-001"
        assert policy_state.content == "Test policy content"
        assert np.array_equal(policy_state.embedding, embedding)
        assert policy_state.version == 2
        assert isinstance(policy_state.timestamp, datetime)


class TestPrincipleState:
    """Test PrincipleState dataclass."""

    def test_principle_state_creation(self):
        """Test principle state creation."""
        embedding = np.array([0.5, 0.6, 0.7, 0.8])
        principle_state = PrincipleState(
            principle_id="PRIN-001",
            content="Test principle content",
            embedding=embedding,
            weight=0.8,
        )

        assert principle_state.principle_id == "PRIN-001"
        assert principle_state.content == "Test principle content"
        assert np.array_equal(principle_state.embedding, embedding)
        assert principle_state.weight == 0.8
        assert isinstance(principle_state.timestamp, datetime)


class TestLipschitzSample:
    """Test LipschitzSample dataclass."""

    def test_lipschitz_sample_creation(self):
        """Test Lipschitz sample creation."""
        sample = LipschitzSample(
            timestamp=datetime.now(timezone.utc),
            lipschitz_constant=0.75,
            policy_distance=0.3,
            principle_distance=0.4,
            sample_size=10,
            stability_level=StabilityLevel.WARNING,
        )

        assert sample.lipschitz_constant == 0.75
        assert sample.policy_distance == 0.3
        assert sample.principle_distance == 0.4
        assert sample.sample_size == 10
        assert sample.stability_level == StabilityLevel.WARNING


class TestStabilityAlert:
    """Test StabilityAlert dataclass."""

    def test_stability_alert_creation(self):
        """Test stability alert creation."""
        alert = StabilityAlert(
            alert_id="WARN-123-0.750",
            timestamp=datetime.now(timezone.utc),
            severity=AlertSeverity.WARNING,
            lipschitz_value=0.75,
            threshold=0.7,
            message="Test warning message",
            affected_policies=["POL-001", "POL-002"],
            recommended_actions=["Review policies", "Check alignment"],
        )

        assert alert.alert_id == "WARN-123-0.750"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.lipschitz_value == 0.75
        assert alert.threshold == 0.7
        assert len(alert.affected_policies) == 2
        assert len(alert.recommended_actions) == 2


class TestLipschitzMonitor:
    """Test LipschitzMonitor functionality."""

    @pytest.fixture
    def monitor(self):
        """Create Lipschitz monitor for testing."""
        return LipschitzMonitor(
            window_size=50,
            warning_threshold=0.7,
            critical_threshold=0.8,
            recalibration_threshold=0.85,
            embedding_model="all-MiniLM-L6-v2",
        )

    @pytest.fixture
    def sample_policy_states(self):
        """Sample policy states for testing."""
        return [
            PolicyState(
                policy_id="POL-001",
                content="Constitutional governance policy ensuring democratic oversight",
                embedding=np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
                version=1,
            ),
            PolicyState(
                policy_id="POL-002",
                content="Financial transparency policy requiring public disclosure",
                embedding=np.array([0.2, 0.3, 0.4, 0.5, 0.6]),
                version=1,
            ),
            PolicyState(
                policy_id="POL-003",
                content="Security protocol policy for system protection",
                embedding=np.array([0.8, 0.7, 0.6, 0.5, 0.4]),
                version=1,
            ),
        ]

    @pytest.fixture
    def sample_principle_states(self):
        """Sample principle states for testing."""
        return [
            PrincipleState(
                principle_id="PRIN-001",
                content="Democratic governance principle ensuring stakeholder participation",
                embedding=np.array([0.15, 0.25, 0.35, 0.45, 0.55]),
                weight=0.9,
            ),
            PrincipleState(
                principle_id="PRIN-002",
                content="Transparency principle requiring open information access",
                embedding=np.array([0.25, 0.35, 0.45, 0.55, 0.65]),
                weight=0.8,
            ),
            PrincipleState(
                principle_id="PRIN-003",
                content="Security principle protecting system integrity",
                embedding=np.array([0.75, 0.65, 0.55, 0.45, 0.35]),
                weight=0.95,
            ),
        ]

    def test_monitor_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.window_size == 50
        assert monitor.warning_threshold == 0.7
        assert monitor.critical_threshold == 0.8
        assert monitor.recalibration_threshold == 0.85
        assert len(monitor.lipschitz_samples) == 0
        assert len(monitor.policy_states) == 0
        assert len(monitor.principle_states) == 0
        assert len(monitor.alert_history) == 0

    @pytest.mark.asyncio
    async def test_initialize_embedding_model_mock(self, monitor):
        """Test embedding model initialization with mock."""
        # Test without actual model (should use mock)
        await monitor.initialize_embedding_model()

        # Should still be able to generate embeddings
        embedding = monitor._get_embedding("test text")
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) > 0
        assert np.linalg.norm(embedding) > 0  # Should be normalized

    def test_generate_mock_embedding(self, monitor):
        """Test mock embedding generation."""
        text1 = "test text one"
        text2 = "test text two"
        text3 = "test text one"  # Same as text1

        embedding1 = monitor._generate_mock_embedding(text1)
        embedding2 = monitor._generate_mock_embedding(text2)
        embedding3 = monitor._generate_mock_embedding(text3)

        # Check properties
        assert isinstance(embedding1, np.ndarray)
        assert len(embedding1) == 32  # Based on hash conversion
        assert abs(np.linalg.norm(embedding1) - 1.0) < 0.001  # Should be normalized

        # Same text should produce same embedding
        assert np.array_equal(embedding1, embedding3)

        # Different text should produce different embeddings
        assert not np.array_equal(embedding1, embedding2)

    def test_calculate_semantic_distance(self, monitor):
        """Test semantic distance calculation."""
        embedding1 = np.array([1.0, 0.0, 0.0])
        embedding2 = np.array([0.0, 1.0, 0.0])
        embedding3 = np.array([1.0, 0.0, 0.0])  # Same as embedding1

        # Distance between orthogonal vectors should be 1.0
        distance1 = monitor._calculate_semantic_distance(embedding1, embedding2)
        assert abs(distance1 - 1.0) < 0.001

        # Distance between identical vectors should be 0.0
        distance2 = monitor._calculate_semantic_distance(embedding1, embedding3)
        assert abs(distance2 - 0.0) < 0.001

        # Distance should be symmetric
        distance3 = monitor._calculate_semantic_distance(embedding2, embedding1)
        assert abs(distance1 - distance3) < 0.001

    @pytest.mark.asyncio
    async def test_update_policy_state(self, monitor):
        """Test policy state update."""
        result = await monitor.update_policy_state(
            "POL-TEST", "Test policy content", version=2
        )

        assert result is True
        assert "POL-TEST" in monitor.policy_states

        policy_state = monitor.policy_states["POL-TEST"]
        assert policy_state.policy_id == "POL-TEST"
        assert policy_state.content == "Test policy content"
        assert policy_state.version == 2
        assert policy_state.embedding is not None
        assert isinstance(policy_state.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_update_principle_state(self, monitor):
        """Test principle state update."""
        result = await monitor.update_principle_state(
            "PRIN-TEST", "Test principle content", weight=0.85
        )

        assert result is True
        assert "PRIN-TEST" in monitor.principle_states

        principle_state = monitor.principle_states["PRIN-TEST"]
        assert principle_state.principle_id == "PRIN-TEST"
        assert principle_state.content == "Test principle content"
        assert principle_state.weight == 0.85
        assert principle_state.embedding is not None
        assert isinstance(principle_state.timestamp, datetime)

    def test_calculate_policy_distances(self, monitor, sample_policy_states):
        """Test policy distance calculation."""
        # Add policy states to monitor
        for policy_state in sample_policy_states:
            monitor.policy_states[policy_state.policy_id] = policy_state

        distances = monitor._calculate_policy_distances()

        # Should have 3 policies, so 3 choose 2 = 3 pairwise distances
        assert len(distances) == 3

        # All distances should be non-negative
        for distance in distances:
            assert distance >= 0.0
            assert distance <= 2.0  # Maximum cosine distance

    def test_calculate_principle_distances(self, monitor, sample_principle_states):
        """Test principle distance calculation."""
        # Add principle states to monitor
        for principle_state in sample_principle_states:
            monitor.principle_states[principle_state.principle_id] = principle_state

        distances = monitor._calculate_principle_distances()

        # Should have 3 principles, so 3 choose 2 = 3 pairwise distances
        assert len(distances) == 3

        # All distances should be non-negative and weighted
        for distance in distances:
            assert distance >= 0.0
            # Weighted distances can be higher than 2.0 due to weighting

    @pytest.mark.asyncio
    async def test_calculate_lipschitz_constant_insufficient_data(self, monitor):
        """Test Lipschitz calculation with insufficient data."""
        # Add only one policy (need at least 2)
        await monitor.update_policy_state("POL-001", "Single policy")

        result = await monitor.calculate_lipschitz_constant()
        assert result is None

    @pytest.mark.asyncio
    async def test_calculate_lipschitz_constant_success(
        self, monitor, sample_policy_states, sample_principle_states
    ):
        """Test successful Lipschitz constant calculation."""
        # Add sufficient data
        for policy_state in sample_policy_states:
            await monitor.update_policy_state(
                policy_state.policy_id, policy_state.content, policy_state.version
            )

        for principle_state in sample_principle_states:
            await monitor.update_principle_state(
                principle_state.principle_id,
                principle_state.content,
                principle_state.weight,
            )

        result = await monitor.calculate_lipschitz_constant()

        assert result is not None
        assert isinstance(result, LipschitzSample)
        assert 0.0 <= result.lipschitz_constant <= 2.0
        assert result.policy_distance >= 0.0
        assert result.principle_distance >= 0.0
        assert result.sample_size > 0
        assert result.stability_level in [
            StabilityLevel.STABLE,
            StabilityLevel.MODERATE,
            StabilityLevel.WARNING,
            StabilityLevel.CRITICAL,
        ]

        # Check that sample was added to window
        assert len(monitor.lipschitz_samples) == 1
        assert monitor.lipschitz_samples[0] == result

    @pytest.mark.asyncio
    async def test_stability_alert_generation(
        self, monitor, sample_policy_states, sample_principle_states
    ):
        """Test stability alert generation."""
        # Setup data
        for policy_state in sample_policy_states:
            await monitor.update_policy_state(
                policy_state.policy_id, policy_state.content
            )

        for principle_state in sample_principle_states:
            await monitor.update_principle_state(
                principle_state.principle_id, principle_state.content
            )

        # Create a sample that should trigger warning
        warning_sample = LipschitzSample(
            timestamp=datetime.now(timezone.utc),
            lipschitz_constant=0.75,  # Above warning threshold (0.7)
            policy_distance=0.3,
            principle_distance=0.4,
            sample_size=6,
            stability_level=StabilityLevel.WARNING,
        )

        initial_alert_count = len(monitor.alert_history)
        await monitor._check_stability_alerts(warning_sample)

        # Should have generated an alert
        assert len(monitor.alert_history) > initial_alert_count

        latest_alert = monitor.alert_history[-1]
        assert latest_alert.severity == AlertSeverity.WARNING
        assert latest_alert.lipschitz_value == 0.75
        assert latest_alert.threshold == 0.7
        assert len(latest_alert.recommended_actions) > 0

    @pytest.mark.asyncio
    async def test_critical_alert_generation(
        self, monitor, sample_policy_states, sample_principle_states
    ):
        """Test critical alert generation."""
        # Setup data
        for policy_state in sample_policy_states:
            await monitor.update_policy_state(
                policy_state.policy_id, policy_state.content
            )

        for principle_state in sample_principle_states:
            await monitor.update_principle_state(
                principle_state.principle_id, principle_state.content
            )

        # Create a sample that should trigger critical alert
        critical_sample = LipschitzSample(
            timestamp=datetime.now(timezone.utc),
            lipschitz_constant=0.85,  # Above critical threshold (0.8)
            policy_distance=0.5,
            principle_distance=0.6,
            sample_size=6,
            stability_level=StabilityLevel.CRITICAL,
        )

        initial_alert_count = len(monitor.alert_history)
        await monitor._check_stability_alerts(critical_sample)

        # Should have generated an alert
        assert len(monitor.alert_history) > initial_alert_count

        latest_alert = monitor.alert_history[-1]
        assert latest_alert.severity == AlertSeverity.CRITICAL
        assert latest_alert.lipschitz_value == 0.85
        assert latest_alert.threshold == 0.8
        assert "CRITICAL" in latest_alert.message
        assert "IMMEDIATE" in latest_alert.recommended_actions[0]

    @pytest.mark.asyncio
    async def test_recalibration_trigger(self, monitor):
        """Test automatic recalibration trigger."""
        # Add some samples to the window
        for i in range(5):
            sample = LipschitzSample(
                timestamp=datetime.now(timezone.utc),
                lipschitz_constant=0.5,
                policy_distance=0.3,
                principle_distance=0.4,
                sample_size=6,
                stability_level=StabilityLevel.MODERATE,
            )
            monitor.lipschitz_samples.append(sample)

        assert len(monitor.lipschitz_samples) == 5

        # Create sample that triggers recalibration
        recalibration_sample = LipschitzSample(
            timestamp=datetime.now(timezone.utc),
            lipschitz_constant=0.9,  # Above recalibration threshold (0.85)
            policy_distance=0.7,
            principle_distance=0.8,
            sample_size=6,
            stability_level=StabilityLevel.CRITICAL,
        )

        initial_recalibration_count = monitor.monitoring_stats["recalibration_count"]
        await monitor._trigger_recalibration(recalibration_sample)

        # Should have triggered recalibration
        assert (
            monitor.monitoring_stats["recalibration_count"]
            == initial_recalibration_count + 1
        )
        assert len(monitor.lipschitz_samples) == 0  # Window should be cleared

    def test_get_current_stability_status_no_data(self, monitor):
        """Test stability status with no data."""
        status = monitor.get_current_stability_status()

        assert status["status"] == "insufficient_data"
        assert status["lipschitz_constant"] is None
        assert status["stability_level"] is None
        assert status["last_calculation"] is None

    def test_get_current_stability_status_with_data(self, monitor):
        """Test stability status with data."""
        # Add sample data
        sample = LipschitzSample(
            timestamp=datetime.now(timezone.utc),
            lipschitz_constant=0.65,
            policy_distance=0.3,
            principle_distance=0.4,
            sample_size=6,
            stability_level=StabilityLevel.MODERATE,
        )
        monitor.lipschitz_samples.append(sample)
        monitor.policy_states["POL-001"] = PolicyState(
            "POL-001", "content", np.array([1, 2, 3])
        )
        monitor.principle_states["PRIN-001"] = PrincipleState(
            "PRIN-001", "content", np.array([1, 2, 3])
        )

        status = monitor.get_current_stability_status()

        assert status["status"] == "active"
        assert status["lipschitz_constant"] == 0.65
        assert status["stability_level"] == "moderate"
        assert status["trend"] in ["stable", "increasing", "decreasing", "unknown"]
        assert status["sample_count"] == 1
        assert status["policy_count"] == 1
        assert status["principle_count"] == 1
        assert "thresholds" in status
        assert status["thresholds"]["warning"] == 0.7
        assert status["thresholds"]["critical"] == 0.8


class TestLipschitzMonitorIntegration:
    """Integration tests for Lipschitz monitor."""

    @pytest.mark.asyncio
    async def test_global_monitor_singleton(self):
        """Test global monitor singleton pattern."""
        monitor1 = await get_lipschitz_monitor()
        monitor2 = await get_lipschitz_monitor()

        # Should return same instance
        assert monitor1 is monitor2

    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        monitor = await get_lipschitz_monitor(
            window_size=10, warning_threshold=0.6, critical_threshold=0.7
        )

        # Add policies and principles
        policies = [
            ("POL-001", "Democratic governance policy"),
            ("POL-002", "Financial transparency policy"),
            ("POL-003", "Security protocol policy"),
        ]

        principles = [
            ("PRIN-001", "Democratic participation principle", 0.9),
            ("PRIN-002", "Transparency principle", 0.8),
            ("PRIN-003", "Security principle", 0.95),
        ]

        for policy_id, content in policies:
            await monitor.update_policy_state(policy_id, content)

        for principle_id, content, weight in principles:
            await monitor.update_principle_state(principle_id, content, weight)

        # Calculate Lipschitz constant
        sample = await monitor.calculate_lipschitz_constant()

        assert sample is not None
        assert isinstance(sample, LipschitzSample)

        # Get status
        status = monitor.get_current_stability_status()
        assert status["status"] == "active"
        assert status["policy_count"] == 3
        assert status["principle_count"] == 3

        # Get performance metrics
        metrics = monitor.get_performance_metrics()
        assert "monitoring_statistics" in metrics
        assert "current_state" in metrics
        assert "thresholds" in metrics
        assert "performance_targets" in metrics


if __name__ == "__main__":
    pytest.main(
        [__file__, "-v", "--cov=lipschitz_monitor", "--cov-report=term-missing"]
    )
