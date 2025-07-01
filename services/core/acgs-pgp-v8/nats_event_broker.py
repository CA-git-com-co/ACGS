#!/usr/bin/env python3
"""
NATS Event Broker for ACGS-PGP v8

Provides centralized event-driven communication for ACGS platform:
- NATS message broker integration
- Event routing and subscription management
- Constitutional compliance event handling
- Real-time analytics event processing
- Service-to-service communication

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import signal
import warnings
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

warnings.filterwarnings("ignore")

# NATS integration
try:
    import nats
    from nats.aio.client import Client as NATS
    from nats.aio.subscription import Subscription

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    print("⚠️ NATS not available - install with: pip install nats-py")

logger = logging.getLogger(__name__)


@dataclass
class ACGSEvent:
    """Standard ACGS event structure."""

    event_type: str
    timestamp: str
    constitutional_hash: str
    source_service: str
    target_service: str | None
    event_id: str
    payload: dict[str, Any]
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    correlation_id: str | None = None


class NATSEventBroker:
    """NATS-based event broker for ACGS platform."""

    def __init__(
        self,
        nats_url: str = "nats://localhost:4222",
        cluster_name: str = "acgs-cluster",
    ):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.nats_url = nats_url
        self.cluster_name = cluster_name
        self.nats_client: NATS | None = None
        self.subscriptions: dict[str, Subscription] = {}
        self.event_handlers: dict[str, list[Callable]] = {}
        self.running = False

        # ACGS event subjects
        self.subjects = {
            # Data Quality Events
            "quality_alert": "acgs.quality.alert.*",
            "quality_degradation": "acgs.quality.degradation.*",
            # Drift Detection Events
            "drift_detected": "acgs.drift.detected.*",
            "retraining_required": "acgs.drift.retraining.*",
            # Constitutional Compliance Events
            "compliance_violation": "acgs.compliance.violation.*",
            "compliance_remediation": "acgs.compliance.remediation.*",
            # Performance Events
            "performance_alert": "acgs.performance.alert.*",
            "service_health": "acgs.service.health.*",
            # System Events
            "service_startup": "acgs.system.startup.*",
            "service_shutdown": "acgs.system.shutdown.*",
            "configuration_change": "acgs.system.config.*",
        }

        logger.info("NATS Event Broker initialized")
        logger.info(f"Constitutional hash: {self.constitutional_hash}")
        logger.info(f"NATS URL: {self.nats_url}")

    async def connect(self) -> bool:
        """Connect to NATS server."""
        if not NATS_AVAILABLE:
            logger.error("❌ NATS not available - cannot connect")
            return False

        try:
            self.nats_client = await nats.connect(
                servers=[self.nats_url],
                name=f"acgs-event-broker-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                max_reconnect_attempts=10,
                reconnect_time_wait=2,
            )

            logger.info(f"✅ Connected to NATS at {self.nats_url}")
            self.running = True

            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            return False

    async def disconnect(self):
        """Disconnect from NATS server."""
        if self.nats_client:
            self.running = False

            # Unsubscribe from all subjects
            for subject, subscription in self.subscriptions.items():
                await subscription.unsubscribe()
                logger.info(f"Unsubscribed from {subject}")

            await self.nats_client.close()
            logger.info("✅ Disconnected from NATS")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum} - initiating graceful shutdown")
        self.running = False

    async def publish_event(
        self,
        subject: str,
        event: ACGSEvent | dict[str, Any],
        reply_to: str | None = None,
    ) -> bool:
        """Publish event to NATS subject."""
        if not self.nats_client:
            logger.error("❌ Not connected to NATS")
            return False

        try:
            # Convert event to JSON
            if isinstance(event, ACGSEvent):
                event_data = asdict(event)
            else:
                event_data = event

            event_json = json.dumps(event_data, default=str)

            # Publish event
            await self.nats_client.publish(subject, event_json.encode(), reply=reply_to)

            logger.info(f"📡 Published event to {subject}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to publish event to {subject}: {e}")
            return False

    async def subscribe_to_subject(
        self, subject: str, handler: Callable, queue_group: str | None = None
    ) -> bool:
        """Subscribe to NATS subject with event handler."""
        if not self.nats_client:
            logger.error("❌ Not connected to NATS")
            return False

        try:

            async def message_handler(msg):
                try:
                    # Parse event data
                    event_data = json.loads(msg.data.decode())

                    # Validate constitutional hash if present
                    if "constitutional_hash" in event_data:
                        if (
                            event_data["constitutional_hash"]
                            != self.constitutional_hash
                        ):
                            logger.warning("⚠️ Constitutional hash mismatch in event")
                            return

                    # Call handler
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data, msg)
                    else:
                        handler(event_data, msg)

                except Exception as e:
                    logger.error(f"❌ Error handling message from {subject}: {e}")

            # Subscribe to subject
            subscription = await self.nats_client.subscribe(
                subject, cb=message_handler, queue=queue_group
            )

            self.subscriptions[subject] = subscription
            logger.info(
                f"✅ Subscribed to {subject}"
                + (f" (queue: {queue_group})" if queue_group else "")
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {subject}: {e}")
            return False

    async def request_response(
        self, subject: str, request_data: dict[str, Any], timeout: float = 5.0
    ) -> dict[str, Any] | None:
        """Send request and wait for response."""
        if not self.nats_client:
            logger.error("❌ Not connected to NATS")
            return None

        try:
            request_json = json.dumps(request_data, default=str)

            # Send request and wait for response
            response = await self.nats_client.request(
                subject, request_json.encode(), timeout=timeout
            )

            # Parse response
            response_data = json.loads(response.data.decode())
            logger.info(f"📨 Received response from {subject}")

            return response_data

        except asyncio.TimeoutError:
            logger.warning(f"⏰ Request to {subject} timed out")
            return None
        except Exception as e:
            logger.error(f"❌ Request to {subject} failed: {e}")
            return None

    async def setup_acgs_event_handlers(self):
        """Set up standard ACGS event handlers."""

        # Data Quality Event Handlers
        await self.subscribe_to_subject(
            self.subjects["quality_alert"],
            self._handle_quality_alert,
            queue_group="acgs-quality-handlers",
        )

        # Drift Detection Event Handlers
        await self.subscribe_to_subject(
            self.subjects["drift_detected"],
            self._handle_drift_detected,
            queue_group="acgs-drift-handlers",
        )

        await self.subscribe_to_subject(
            self.subjects["retraining_required"],
            self._handle_retraining_required,
            queue_group="acgs-retraining-handlers",
        )

        # Constitutional Compliance Event Handlers
        await self.subscribe_to_subject(
            self.subjects["compliance_violation"],
            self._handle_compliance_violation,
            queue_group="acgs-compliance-handlers",
        )

        # Performance Event Handlers
        await self.subscribe_to_subject(
            self.subjects["performance_alert"],
            self._handle_performance_alert,
            queue_group="acgs-performance-handlers",
        )

        # Service Health Event Handlers
        await self.subscribe_to_subject(
            self.subjects["service_health"],
            self._handle_service_health,
            queue_group="acgs-health-handlers",
        )

        logger.info("✅ ACGS event handlers configured")

    # Standard ACGS Event Handlers
    async def _handle_quality_alert(self, event_data: dict[str, Any], msg):
        """Handle data quality alert events."""
        logger.warning(f"🚨 QUALITY ALERT: {event_data.get('service_id', 'unknown')}")
        logger.warning(f"   Score: {event_data.get('quality_score', 0):.3f}")
        logger.warning(f"   Severity: {event_data.get('severity', 'UNKNOWN')}")

        # In production: trigger quality remediation workflows

    async def _handle_drift_detected(self, event_data: dict[str, Any], msg):
        """Handle drift detection events."""
        logger.warning(f"📊 DRIFT DETECTED: {event_data.get('model_id', 'unknown')}")
        logger.warning(f"   Features: {len(event_data.get('features_with_drift', []))}")
        logger.warning(f"   Severity: {event_data.get('drift_severity', 'UNKNOWN')}")

    async def _handle_retraining_required(self, event_data: dict[str, Any], msg):
        """Handle model retraining requirement events."""
        logger.critical(
            f"🔄 RETRAINING REQUIRED: {event_data.get('model_id', 'unknown')}"
        )
        logger.critical(f"   Service: {event_data.get('service_id', 'unknown')}")

        # In production: trigger model retraining pipeline

    async def _handle_compliance_violation(self, event_data: dict[str, Any], msg):
        """Handle constitutional compliance violation events."""
        logger.critical(
            f"⚖️ COMPLIANCE VIOLATION: {event_data.get('service_id', 'unknown')}"
        )
        logger.critical(f"   Score: {event_data.get('compliance_score', 0):.3f}")
        logger.critical(f"   Violations: {len(event_data.get('violations', []))}")

        # In production: trigger compliance remediation

    async def _handle_performance_alert(self, event_data: dict[str, Any], msg):
        """Handle performance alert events."""
        logger.warning(
            f"⚡ PERFORMANCE ALERT: {event_data.get('service_id', 'unknown')}"
        )
        logger.warning(f"   Metric: {event_data.get('metric', 'unknown')}")
        logger.warning(f"   Value: {event_data.get('value', 'unknown')}")

    async def _handle_service_health(self, event_data: dict[str, Any], msg):
        """Handle service health events."""
        service_id = event_data.get("service_id", "unknown")
        status = event_data.get("status", "unknown")

        if status == "healthy":
            logger.info(f"✅ Service healthy: {service_id}")
        else:
            logger.warning(f"❌ Service unhealthy: {service_id}")

    async def run_event_loop(self):
        """Run the main event processing loop."""
        logger.info("🚀 Starting NATS event broker loop")

        while self.running:
            try:
                # Keep the event loop running
                await asyncio.sleep(1)

                # Periodic health check
                if self.nats_client and not self.nats_client.is_connected:
                    logger.warning("⚠️ NATS connection lost - attempting reconnect")
                    await self.connect()

            except Exception as e:
                logger.error(f"❌ Error in event loop: {e}")
                await asyncio.sleep(5)

        logger.info("✅ Event broker loop stopped")


# Example usage
async def main():
    """Main function to run NATS event broker."""

    # Initialize event broker
    broker = NATSEventBroker()

    # Connect to NATS
    if not await broker.connect():
        logger.error("❌ Failed to connect to NATS - exiting")
        return

    # Set up ACGS event handlers
    await broker.setup_acgs_event_handlers()

    # Run event processing loop
    try:
        await broker.run_event_loop()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await broker.disconnect()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run event broker
    asyncio.run(main())
