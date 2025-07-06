#!/usr/bin/env python3
"""
ACGS Enterprise Streaming Infrastructure - Complete Example

This example demonstrates how to use the complete Apache Kafka enterprise
streaming infrastructure for the Advanced Constitutional Governance System,
implementing the ACGE technical validation recommendations.

Features demonstrated:
- Event streaming with constitutional compliance validation
- Multi-broker Kafka cluster with high availability
- NATS integration for lightweight messaging
- Dead letter queue handling and error recovery
- Real-time monitoring and alerting
- Stream processing with constitutional compliance checks
"""
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

# Import ACGS streaming components
from event_streaming_manager import (
    EventPriority,
    EventRoutingStrategy,
    EventStreamingManager,
    EventType,
    StreamingEvent,
)
from kafka_config_manager import EnvironmentType, KafkaConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ACGSStreamingDemo:
    """
    Demonstration of ACGS Enterprise Streaming Infrastructure
    """

    def __init__(self):
        self.streaming_manager = None
        self.config_manager = None
        self.running = False

        # Demo configuration
        self.config = {
            "cluster_id": "acgs-main",
            "environment": "development",
            "default_routing_strategy": "hybrid",
            "nats_servers": ["nats://localhost:4222"],
        }

        # Event counters for demo
        self.events_sent = 0
        self.events_received = 0
        self.constitutional_violations = 0

    async def initialize(self) -> bool:
        """Initialize the streaming infrastructure"""
        try:
            logger.info("Initializing ACGS Enterprise Streaming Infrastructure Demo")

            # Initialize configuration manager
            self.config_manager = KafkaConfigManager()

            # Initialize streaming manager
            self.streaming_manager = EventStreamingManager(self.config)
            success = await self.streaming_manager.initialize()

            if not success:
                logger.error("Failed to initialize streaming manager")
                return False

            # Register event handlers
            await self._register_event_handlers()

            logger.info("ACGS Streaming Infrastructure initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    async def _register_event_handlers(self):
        """Register event handlers for different event types"""

        # Constitutional decision handler
        async def constitutional_decision_handler(event: StreamingEvent) -> bool:
            try:
                logger.info(f"Processing constitutional decision: {event.event_id}")

                # Simulate constitutional AI processing
                decision_data = event.payload

                # Check if decision requires human escalation
                if decision_data.get("confidence_score", 1.0) < 0.8:
                    logger.warning(
                        f"Low confidence constitutional decision: {event.event_id}"
                    )
                    await self._escalate_to_human(event)

                # Validate constitutional compliance
                if not event.constitutional_compliant:
                    self.constitutional_violations += 1
                    logger.error(f"Constitutional violation detected: {event.event_id}")
                    return False

                # Process the decision
                await self._process_constitutional_decision(decision_data)

                self.events_received += 1
                return True

            except Exception as e:
                logger.error(f"Constitutional decision handler failed: {e}")
                return False

        # Policy synthesis handler
        async def policy_synthesis_handler(event: StreamingEvent) -> bool:
            try:
                logger.info(f"Processing policy synthesis: {event.event_id}")

                policy_data = event.payload

                # Simulate policy synthesis processing
                await self._synthesize_policy(policy_data)

                self.events_received += 1
                return True

            except Exception as e:
                logger.error(f"Policy synthesis handler failed: {e}")
                return False

        # Audit event handler
        async def audit_event_handler(event: StreamingEvent) -> bool:
            try:
                logger.info(f"Processing audit event: {event.event_id}")

                audit_data = event.payload

                # Store audit event for compliance
                await self._store_audit_event(audit_data)

                self.events_received += 1
                return True

            except Exception as e:
                logger.error(f"Audit event handler failed: {e}")
                return False

        # Register handlers
        await self.streaming_manager.subscribe_to_events(
            EventType.CONSTITUTIONAL_DECISION, constitutional_decision_handler
        )
        await self.streaming_manager.subscribe_to_events(
            EventType.POLICY_SYNTHESIS, policy_synthesis_handler
        )
        await self.streaming_manager.subscribe_to_events(
            EventType.AUDIT_EVENT, audit_event_handler
        )

    async def run_demo(self):
        """Run the complete streaming infrastructure demo"""
        try:
            logger.info("Starting ACGS Streaming Infrastructure Demo")
            self.running = True

            # Start concurrent demo tasks
            demo_tasks = [
                self._constitutional_ai_simulation(),
                self._policy_synthesis_simulation(),
                self._audit_logging_simulation(),
                self._monitoring_simulation(),
                self._metrics_reporter(),
            ]

            # Run demo tasks concurrently
            await asyncio.gather(*demo_tasks)

        except KeyboardInterrupt:
            logger.info("Demo interrupted by user")
        except Exception as e:
            logger.error(f"Demo failed: {e}")
        finally:
            self.running = False
            await self._cleanup()

    async def _constitutional_ai_simulation(self):
        """Simulate constitutional AI decision making"""
        while self.running:
            try:
                # Create constitutional decision event
                decision_event = StreamingEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.CONSTITUTIONAL_DECISION,
                    priority=EventPriority.HIGH,
                    source_service="constitutional-ai-service",
                    target_service="governance-orchestrator",
                    payload={
                        "decision_id": str(uuid.uuid4()),
                        "prompt": "Should AI system proceed with this action?",
                        "response": "Yes, action aligns with constitutional principles",
                        "confidence_score": 0.95,
                        "principles_applied": [
                            "transparency",
                            "fairness",
                            "accountability",
                        ],
                        "reasoning": (
                            "Action promotes democratic participation and transparency"
                        ),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    metadata={
                        "model_version": "constitutional-ai-v2.1",
                        "evaluation_time_ms": 150,
                        "requires_audit": True,
                    },
                    routing_strategy=EventRoutingStrategy.HYBRID,
                    constitutional_compliant=True,
                    correlation_id=f"const-{uuid.uuid4()}",
                    timestamp=datetime.utcnow(),
                    ttl_seconds=3600,
                )

                # Occasionally create non-compliant events for testing
                if self.events_sent % 10 == 0:
                    decision_event.constitutional_compliant = False
                    decision_event.payload["confidence_score"] = 0.3

                # Publish event
                success = await self.streaming_manager.publish_event(decision_event)
                if success:
                    self.events_sent += 1
                    logger.info(
                        "Published constitutional decision event:"
                        f" {decision_event.event_id}"
                    )
                else:
                    logger.error(
                        "Failed to publish constitutional decision event:"
                        f" {decision_event.event_id}"
                    )

                await asyncio.sleep(5)  # New decision every 5 seconds

            except Exception as e:
                logger.error(f"Constitutional AI simulation failed: {e}")
                await asyncio.sleep(10)

    async def _policy_synthesis_simulation(self):
        """Simulate policy synthesis events"""
        while self.running:
            try:
                # Create policy synthesis event
                synthesis_event = StreamingEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.POLICY_SYNTHESIS,
                    priority=EventPriority.MEDIUM,
                    source_service="governance-synthesis-service",
                    target_service="policy-enforcement",
                    payload={
                        "policy_id": str(uuid.uuid4()),
                        "domain": "data_privacy",
                        "synthesized_rule": (
                            "Personal data must be encrypted at rest and in transit"
                        ),
                        "confidence": 0.88,
                        "source_principles": [
                            "privacy",
                            "security",
                            "data_minimization",
                        ],
                        "affected_services": ["user-service", "data-service"],
                        "effective_date": (
                            datetime.utcnow() + timedelta(days=7)
                        ).isoformat(),
                    },
                    metadata={
                        "synthesis_method": "llm_multi_model_consensus",
                        "validation_status": "pending",
                        "stakeholder_review_required": True,
                    },
                    routing_strategy=EventRoutingStrategy.KAFKA_ONLY,
                    constitutional_compliant=True,
                    correlation_id=f"policy-{uuid.uuid4()}",
                    timestamp=datetime.utcnow(),
                    ttl_seconds=7200,
                )

                # Publish event
                success = await self.streaming_manager.publish_event(synthesis_event)
                if success:
                    self.events_sent += 1
                    logger.info(
                        f"Published policy synthesis event: {synthesis_event.event_id}"
                    )

                await asyncio.sleep(8)  # New policy every 8 seconds

            except Exception as e:
                logger.error(f"Policy synthesis simulation failed: {e}")
                await asyncio.sleep(15)

    async def _audit_logging_simulation(self):
        """Simulate audit event generation"""
        while self.running:
            try:
                # Create audit event
                audit_event = StreamingEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.AUDIT_EVENT,
                    priority=EventPriority.LOW,
                    source_service="various-services",
                    target_service="audit-service",
                    payload={
                        "user_id": f"user_{uuid.uuid4().hex[:8]}",
                        "action": "view_constitutional_decision",
                        "resource": "constitutional_decision_history",
                        "ip_address": "192.168.1.100",
                        "user_agent": "ACGS-WebUI/1.0",
                        "result": "success",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    metadata={
                        "session_id": str(uuid.uuid4()),
                        "compliance_level": "standard",
                        "retention_period_days": 2555,  # 7 years
                    },
                    routing_strategy=EventRoutingStrategy.KAFKA_ONLY,
                    constitutional_compliant=True,
                    correlation_id=None,
                    timestamp=datetime.utcnow(),
                    ttl_seconds=None,  # Permanent retention
                )

                # Publish event
                success = await self.streaming_manager.publish_event(audit_event)
                if success:
                    self.events_sent += 1
                    logger.info(f"Published audit event: {audit_event.event_id}")

                await asyncio.sleep(3)  # Frequent audit events

            except Exception as e:
                logger.error(f"Audit logging simulation failed: {e}")
                await asyncio.sleep(10)

    async def _monitoring_simulation(self):
        """Simulate system monitoring events"""
        while self.running:
            try:
                # Create monitoring/metrics event
                metric_event = StreamingEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.METRIC_EVENT,
                    priority=EventPriority.LOW,
                    source_service="monitoring-service",
                    target_service="metrics-collector",
                    payload={
                        "metric_name": "constitutional_ai_response_time",
                        "metric_value": 145.7,
                        "metric_unit": "milliseconds",
                        "service": "constitutional-ai-service",
                        "timestamp": datetime.utcnow().isoformat(),
                        "tags": {
                            "environment": "development",
                            "model_version": "v2.1",
                            "instance": "constitutional-ai-1",
                        },
                    },
                    metadata={"collection_interval": 30, "aggregation_window": "1m"},
                    routing_strategy=EventRoutingStrategy.NATS_ONLY,
                    constitutional_compliant=True,
                    correlation_id=None,
                    timestamp=datetime.utcnow(),
                    ttl_seconds=86400,  # 24 hours
                )

                # Publish event
                success = await self.streaming_manager.publish_event(metric_event)
                if success:
                    self.events_sent += 1

                await asyncio.sleep(30)  # Metrics every 30 seconds

            except Exception as e:
                logger.error(f"Monitoring simulation failed: {e}")
                await asyncio.sleep(60)

    async def _metrics_reporter(self):
        """Report demo metrics periodically"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Report every minute

                # Get streaming manager metrics
                streaming_metrics = self.streaming_manager.get_metrics_summary()

                logger.info("=== ACGS Streaming Demo Metrics ===")
                logger.info(f"Events Sent: {self.events_sent}")
                logger.info(f"Events Received: {self.events_received}")
                logger.info(
                    f"Constitutional Violations: {self.constitutional_violations}"
                )
                logger.info(f"Health Status: {streaming_metrics['health_status']}")
                logger.info(
                    f"Circuit Breakers: {streaming_metrics['circuit_breaker_status']}"
                )
                logger.info("===================================")

            except Exception as e:
                logger.error(f"Metrics reporting failed: {e}")

    async def _process_constitutional_decision(self, decision_data: dict[str, Any]):
        """Process a constitutional decision (simulation)"""
        decision_id = decision_data["decision_id"]
        confidence = decision_data["confidence_score"]

        if confidence > 0.9:
            logger.info(
                f"High confidence constitutional decision {decision_id} -"
                " auto-approving"
            )
        elif confidence > 0.7:
            logger.info(
                f"Medium confidence constitutional decision {decision_id} - reviewing"
            )
        else:
            logger.warning(
                f"Low confidence constitutional decision {decision_id} - escalating"
            )

    async def _escalate_to_human(self, event: StreamingEvent):
        """Escalate low-confidence decisions to human review"""
        escalation_event = StreamingEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.ALERT_EVENT,
            priority=EventPriority.HIGH,
            source_service="constitutional-ai-service",
            target_service="human-review-service",
            payload={
                "original_event_id": event.event_id,
                "escalation_reason": "low_confidence_constitutional_decision",
                "requires_human_review": True,
                "urgency": "medium",
                "estimated_review_time_hours": 2,
            },
            metadata={
                "original_event": event.payload,
                "escalation_timestamp": datetime.utcnow().isoformat(),
            },
            routing_strategy=EventRoutingStrategy.HYBRID,
            constitutional_compliant=True,
            correlation_id=event.correlation_id,
            timestamp=datetime.utcnow(),
            ttl_seconds=7200,
        )

        await self.streaming_manager.publish_event(escalation_event)
        logger.info(
            f"Escalated constitutional decision {event.event_id} to human review"
        )

    async def _synthesize_policy(self, policy_data: dict[str, Any]):
        """Process policy synthesis (simulation)"""
        policy_id = policy_data["policy_id"]
        domain = policy_data["domain"]
        confidence = policy_data["confidence"]

        logger.info(
            f"Synthesizing policy {policy_id} for domain {domain} with confidence"
            f" {confidence}"
        )

        # Simulate policy validation and storage
        if confidence > 0.85:
            logger.info(f"Policy {policy_id} approved for implementation")
        else:
            logger.info(f"Policy {policy_id} requires additional review")

    async def _store_audit_event(self, audit_data: dict[str, Any]):
        """Store audit event for compliance (simulation)"""
        user_id = audit_data["user_id"]
        action = audit_data["action"]

        logger.info(f"Storing audit event: {user_id} performed {action}")

        # In real implementation, this would store to a compliance database

    async def _cleanup(self):
        """Clean up resources"""
        try:
            if self.streaming_manager:
                logger.info("Shutting down streaming manager...")
                await self.streaming_manager.shutdown()

            logger.info("Cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Configuration validation example
async def validate_kafka_configuration():
    """Demonstrate Kafka configuration validation"""
    logger.info("Validating Kafka configuration...")

    config_manager = KafkaConfigManager()

    # Test cluster configuration
    cluster_config = await config_manager.load_cluster_config(
        "acgs-main", EnvironmentType.DEVELOPMENT
    )

    logger.info(f"Cluster config loaded: {cluster_config.cluster_id}")
    logger.info(f"Bootstrap servers: {cluster_config.bootstrap_servers}")
    logger.info(f"Security protocol: {cluster_config.security_protocol}")

    # Test connection
    connection_ok = await config_manager.test_connection(
        "acgs-main", EnvironmentType.DEVELOPMENT
    )

    logger.info(f"Kafka connection test: {'PASS' if connection_ok else 'FAIL'}")

    return connection_ok


# Main execution
async def main():
    """Main demo execution"""
    logger.info("Starting ACGS Enterprise Streaming Infrastructure Demo")

    try:
        # Validate configuration first
        config_valid = await validate_kafka_configuration()
        if not config_valid:
            logger.warning("Kafka connection test failed - demo may not work properly")
            logger.info(
                "Please ensure Kafka cluster is running (use deploy_kafka.sh start)"
            )

        # Initialize and run demo
        demo = ACGSStreamingDemo()

        success = await demo.initialize()
        if not success:
            logger.error("Demo initialization failed")
            return

        # Run demo for 5 minutes or until interrupted
        logger.info("Demo will run for 5 minutes. Press Ctrl+C to stop early.")

        demo_task = asyncio.create_task(demo.run_demo())
        timeout_task = asyncio.create_task(asyncio.sleep(300))  # 5 minutes

        done, pending = await asyncio.wait(
            [demo_task, timeout_task], return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel remaining tasks
        for task in pending:
            task.cancel()

        logger.info("Demo completed successfully")

    except Exception as e:
        logger.error(f"Demo failed: {e}")

    logger.info("ACGS Enterprise Streaming Infrastructure Demo finished")


if __name__ == "__main__":
    asyncio.run(main())
