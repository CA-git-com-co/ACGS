"""
Integration tests for NATS messaging.

Tests NATS message broker integration including publish/subscribe,
event routing, and JetStream persistence.
"""

import asyncio
import os

# Import messaging components directly to avoid full service dependencies
import sys
from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from dgm_service.messaging.event_publisher import EventPublisher
from dgm_service.messaging.event_subscriber import EventSubscriber
from dgm_service.messaging.message_types import EventPriority, EventType, create_improvement_event
from dgm_service.messaging.nats_client import NATSClient, NATSConfig


@pytest.mark.integration
@pytest.mark.messaging
class TestNATSIntegration:
    """Integration tests for NATS messaging."""

    @pytest.fixture
    def nats_config(self):
        """NATS configuration for testing."""
        return NATSConfig(
            servers=["nats://localhost:4222"],
            name="dgm-service-test",
            enable_jetstream=True,
            stream_name="DGM_EVENTS_TEST",
        )

    @pytest.fixture
    async def mock_nats_client(self, nats_config):
        """Mock NATS client for testing."""
        client = NATSClient(nats_config)

        # Mock the actual NATS connection
        client.nc = AsyncMock()
        client.js = AsyncMock()
        client.connected = True

        # Mock publish method
        async def mock_publish(subject, data, headers=None):
            client.metrics["messages_published"] += 1
            return True

        client.nc.publish = mock_publish
        client.js.publish = mock_publish

        # Mock subscribe method
        async def mock_subscribe(subject, cb, queue=None, config=None):
            subscription = AsyncMock()
            client.subscriptions[subject] = subscription
            return subscription

        client.nc.subscribe = mock_subscribe
        client.js.subscribe = mock_subscribe

        return client

    async def test_nats_client_connection(self, nats_config):
        """Test NATS client connection and configuration."""
        client = NATSClient(nats_config)

        # Mock successful connection
        with patch("nats.connect") as mock_connect:
            mock_nc = AsyncMock()
            mock_connect.return_value = mock_nc

            # Mock JetStream
            mock_js = AsyncMock()
            mock_nc.jetstream.return_value = mock_js
            mock_js.add_stream = AsyncMock()

            success = await client.connect()

            assert success is True
            assert client.connected is True
            assert client.nc is not None

            # Verify connection options
            mock_connect.assert_called_once()
            call_args = mock_connect.call_args[1]
            assert call_args["servers"] == nats_config.servers
            assert call_args["name"] == nats_config.name

    async def test_event_publisher_integration(self, mock_nats_client):
        """Test event publisher with NATS client."""
        publisher = EventPublisher(mock_nats_client)

        # Test improvement event publishing
        success = await publisher.publish_improvement_proposed(
            improvement_id=str(uuid4()),
            strategy="performance_optimization",
            target_services=["gs-service"],
            expected_improvement=0.15,
            risk_level="low",
        )

        assert success is True
        assert publisher.metrics["events_published"] == 1
        assert mock_nats_client.metrics["messages_published"] == 1

    async def test_event_subscriber_integration(self, mock_nats_client):
        """Test event subscriber with NATS client."""
        subscriber = EventSubscriber(mock_nats_client)

        # Test event handler
        received_events = []

        async def test_handler(event_type, event_data, metadata):
            received_events.append({"type": event_type, "data": event_data, "metadata": metadata})

        # Subscribe to improvement events
        success = await subscriber.subscribe_to_event(EventType.IMPROVEMENT_PROPOSED, test_handler)

        assert success is True
        assert subscriber.metrics["handlers_registered"] == 1
        assert subscriber.metrics["active_subscriptions"] == 1

    async def test_publish_subscribe_workflow(self, mock_nats_client):
        """Test complete publish-subscribe workflow."""
        publisher = EventPublisher(mock_nats_client)
        subscriber = EventSubscriber(mock_nats_client)

        # Setup subscriber
        received_events = []

        async def event_handler(event_type, event_data, metadata):
            received_events.append({"type": event_type, "data": event_data, "metadata": metadata})

        await subscriber.subscribe_to_improvements(event_handler)

        # Publish events
        improvement_id = str(uuid4())

        # Publish proposal
        await publisher.publish_improvement_proposed(
            improvement_id=improvement_id,
            strategy="performance_optimization",
            target_services=["gs-service"],
            expected_improvement=0.15,
            risk_level="low",
        )

        # Publish execution
        await publisher.publish_improvement_executed(
            improvement_id=improvement_id,
            strategy="performance_optimization",
            actual_improvement=0.12,
            execution_time=45.2,
            constitutional_compliance_score=0.95,
        )

        # Verify publishing metrics
        assert publisher.metrics["events_published"] == 2
        assert mock_nats_client.metrics["messages_published"] == 2

    async def test_performance_event_publishing(self, mock_nats_client):
        """Test performance event publishing."""
        publisher = EventPublisher(mock_nats_client)

        # Publish performance metrics
        success = await publisher.publish_performance_metrics(
            metric_name="response_time",
            metric_value=125.5,
            service_name="dgm-service",
            baseline_value=150.0,
            improvement_percentage=16.3,
        )

        assert success is True

        # Publish performance alert
        success = await publisher.publish_performance_alert(
            metric_name="error_rate",
            metric_value=0.05,
            service_name="gs-service",
            alert_level="warning",
            threshold_value=0.02,
        )

        assert success is True
        assert publisher.metrics["events_published"] == 2

    async def test_constitutional_event_publishing(self, mock_nats_client):
        """Test constitutional event publishing."""
        publisher = EventPublisher(mock_nats_client)

        improvement_id = str(uuid4())

        # Publish assessment completion
        success = await publisher.publish_constitutional_assessment(
            improvement_id=improvement_id,
            compliance_score=0.95,
            constitutional_hash="cdd01ef066bc6cf2",
            assessment_type="proposal",
            violations=[],
        )

        assert success is True

        # Publish violation detection
        success = await publisher.publish_constitutional_violation(
            improvement_id=improvement_id,
            compliance_score=0.65,
            violations=[
                {
                    "type": "safety_concern",
                    "severity": "medium",
                    "description": "Insufficient safety constraints",
                }
            ],
            remediation_required=True,
        )

        assert success is True
        assert publisher.metrics["events_published"] == 2

    async def test_bandit_event_publishing(self, mock_nats_client):
        """Test bandit algorithm event publishing."""
        publisher = EventPublisher(mock_nats_client)

        # Publish arm selection
        success = await publisher.publish_bandit_arm_selected(
            algorithm_type="UCB1",
            arm_name="performance_optimization",
            arm_pulls=25,
            confidence_bound=0.85,
            action_taken="exploit",
        )

        assert success is True

        # Publish reward update
        success = await publisher.publish_bandit_reward_updated(
            algorithm_type="UCB1",
            arm_name="performance_optimization",
            arm_rewards=18.5,
            arm_success_rate=0.74,
            total_pulls=50,
            average_reward=0.72,
        )

        assert success is True
        assert publisher.metrics["events_published"] == 2

    async def test_event_routing_and_subjects(self, mock_nats_client):
        """Test event routing to correct NATS subjects."""
        publisher = EventPublisher(mock_nats_client)

        # Track published subjects
        published_subjects = []

        async def mock_publish(subject, data, headers=None):
            published_subjects.append(subject)
            return True

        mock_nats_client.nc.publish = mock_publish
        mock_nats_client.js.publish = mock_publish

        # Publish different event types
        await publisher.publish_improvement_proposed(
            improvement_id=str(uuid4()),
            strategy="test",
            target_services=["test"],
            expected_improvement=0.1,
            risk_level="low",
        )

        await publisher.publish_performance_metrics(
            metric_name="test_metric", metric_value=100.0, service_name="test-service"
        )

        await publisher.publish_constitutional_assessment(
            improvement_id=str(uuid4()),
            compliance_score=0.9,
            constitutional_hash="test_hash",
            assessment_type="test",
        )

        # Verify correct subject routing
        assert "dgm.improvement.proposed" in published_subjects
        assert "dgm.performance.metrics.updated" in published_subjects
        assert "dgm.constitutional.assessment.completed" in published_subjects

    async def test_subscriber_pattern_matching(self, mock_nats_client):
        """Test subscriber pattern matching."""
        subscriber = EventSubscriber(mock_nats_client)

        received_events = []

        async def pattern_handler(subject, event_data, metadata):
            received_events.append({"subject": subject, "data": event_data, "metadata": metadata})

        # Subscribe to pattern
        success = await subscriber.subscribe_to_pattern(
            "dgm.improvement.*", pattern_handler, queue_group="dgm-improvements"
        )

        assert success is True
        assert subscriber.metrics["active_subscriptions"] == 1

    async def test_error_handling_and_retries(self, mock_nats_client):
        """Test error handling and retry mechanisms."""
        publisher = EventPublisher(mock_nats_client)

        # Mock publish failure
        async def mock_failing_publish(subject, data, headers=None):
            raise Exception("NATS connection error")

        mock_nats_client.nc.publish = mock_failing_publish
        mock_nats_client.js.publish = mock_failing_publish

        # Attempt to publish
        success = await publisher.publish_improvement_proposed(
            improvement_id=str(uuid4()),
            strategy="test",
            target_services=["test"],
            expected_improvement=0.1,
            risk_level="low",
        )

        assert success is False
        assert publisher.metrics["events_failed"] == 1

    async def test_health_check_integration(self, mock_nats_client):
        """Test NATS health check integration."""
        # Mock server info
        mock_nats_client.nc.server_info = {
            "server_id": "test_server",
            "version": "2.10.0",
            "max_payload": 1048576,
        }

        # Mock RTT
        mock_nats_client.nc.rtt = AsyncMock(return_value=0.001)

        health = await mock_nats_client.health_check()

        assert health["connected"] is True
        assert health["jetstream_enabled"] is True
        assert health["server_info"]["server_id"] == "test_server"
        assert health["rtt_ms"] == 1.0

    async def test_concurrent_publishing(self, mock_nats_client):
        """Test concurrent event publishing."""
        publisher = EventPublisher(mock_nats_client)

        # Create multiple concurrent publishing tasks
        tasks = []
        for i in range(10):
            task = publisher.publish_improvement_proposed(
                improvement_id=str(uuid4()),
                strategy=f"strategy_{i}",
                target_services=[f"service_{i}"],
                expected_improvement=0.1 + i * 0.01,
                risk_level="low",
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # Verify all published successfully
        assert all(results)
        assert publisher.metrics["events_published"] == 10
        assert mock_nats_client.metrics["messages_published"] == 10
