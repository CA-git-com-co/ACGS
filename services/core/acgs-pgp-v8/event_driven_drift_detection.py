#!/usr/bin/env python3
"""
Event-Driven Drift Detection Framework for ACGS-PGP v8

Extends the existing drift detection framework with event-driven capabilities:
- Real-time drift monitoring with streaming data
- Automated model retraining triggers
- NATS message broker integration for drift events
- Async/await patterns for non-blocking operations
- Event-driven threshold management

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import warnings
from collections.abc import AsyncGenerator, Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Import existing drift detection framework
from data_drift_detection import DataDriftDetector, DriftDetectionResult

# NATS integration (placeholder)
try:
    import nats
    from nats.aio.client import Client as NATS

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DriftEvent:
    """Drift detection event for message broker publishing."""

    event_type: str
    timestamp: str
    constitutional_hash: str
    model_id: str
    service_id: str
    drift_detected: bool
    retraining_required: bool
    features_with_drift: list[str]
    drift_severity: str
    metadata: dict[str, Any]


class EventDrivenDriftDetector:
    """Event-driven drift detection framework with real-time monitoring."""

    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.nats_url = nats_url
        self.nats_client: NATS | None = None
        self.drift_detector = DataDriftDetector()

        # Reference datasets for drift comparison
        self.reference_datasets: dict[str, pd.DataFrame] = {}

        # Drift monitoring configuration
        self.monitoring_config = {
            "window_size": 1000,  # Size of data window for drift detection
            "monitoring_interval": 30,  # Seconds between drift checks
            "drift_threshold": 0.05,  # KS test p-value threshold
            "retraining_threshold": 3,  # Number of drifted features to trigger retraining
        }

        # Event handlers registry
        self.event_handlers: dict[str, list[Callable]] = {
            "drift_detected": [],
            "retraining_required": [],
            "model_updated": [],
            "drift_resolved": [],
        }

        logger.info("Event-driven drift detector initialized")
        logger.info(f"Constitutional hash: {self.constitutional_hash}")

    async def connect_to_nats(self) -> bool:
        """Connect to NATS message broker."""
        if not NATS_AVAILABLE:
            logger.warning("NATS not available - using mock mode")
            return False

        try:
            self.nats_client = await nats.connect(self.nats_url)
            logger.info(f"✅ Connected to NATS at {self.nats_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            return False

    async def disconnect_from_nats(self):
        """Disconnect from NATS message broker."""
        if self.nats_client:
            await self.nats_client.close()
            logger.info("Disconnected from NATS")

    def register_reference_dataset(self, model_id: str, reference_data: pd.DataFrame):
        """Register reference dataset for a specific model."""
        self.reference_datasets[model_id] = reference_data.copy()
        logger.info(
            f"Registered reference dataset for {model_id}: {len(reference_data)} records"
        )

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler for specific event types."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type} events")

    async def publish_drift_event(self, event: DriftEvent):
        """Publish drift event to NATS message broker."""
        event_data = asdict(event)
        event_json = json.dumps(event_data, default=str)

        # Determine NATS subject based on event type and severity
        subject = f"acgs.drift.{event.event_type}.{event.drift_severity.lower()}"

        if self.nats_client:
            try:
                await self.nats_client.publish(subject, event_json.encode())
                logger.info(f"📡 Published drift event to {subject}")
            except Exception as e:
                logger.error(f"❌ Failed to publish drift event: {e}")
        else:
            # Mock mode - just log the event
            logger.info(f"📡 [MOCK] Would publish to {subject}: {event.event_type}")

        # Trigger local event handlers
        await self._trigger_local_handlers(event)

    async def _trigger_local_handlers(self, event: DriftEvent):
        """Trigger local event handlers."""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"❌ Drift event handler failed: {e}")

    async def detect_drift_async(
        self, current_data: pd.DataFrame, model_id: str, service_id: str = "unknown"
    ) -> DriftDetectionResult:
        """Perform async drift detection with event publishing."""

        if model_id not in self.reference_datasets:
            raise ValueError(f"No reference dataset registered for model {model_id}")

        reference_data = self.reference_datasets[model_id]

        logger.info(f"Starting async drift detection for {model_id}")

        # Perform drift detection (non-blocking)
        drift_result = await asyncio.get_event_loop().run_in_executor(
            None,
            self.drift_detector.comprehensive_drift_analysis,
            reference_data,
            current_data,
        )

        # Determine drift severity
        drift_severity = self._determine_drift_severity(drift_result)

        # Create drift event
        drift_event = DriftEvent(
            event_type=(
                "drift_detected" if drift_result.drift_detected else "drift_check"
            ),
            timestamp=datetime.now().isoformat(),
            constitutional_hash=self.constitutional_hash,
            model_id=model_id,
            service_id=service_id,
            drift_detected=drift_result.drift_detected,
            retraining_required=drift_result.retraining_required,
            features_with_drift=drift_result.features_with_ks_drift
            + drift_result.features_with_psi_drift,
            drift_severity=drift_severity,
            metadata={
                "ks_drift_features": len(drift_result.features_with_ks_drift),
                "psi_drift_features": len(drift_result.features_with_psi_drift),
                "current_data_size": len(current_data),
                "reference_data_size": len(reference_data),
            },
        )

        # Publish event if drift detected or retraining required
        if drift_result.drift_detected or drift_result.retraining_required:
            await self.publish_drift_event(drift_event)

            # Trigger retraining event if required
            if drift_result.retraining_required:
                await self._trigger_retraining_event(drift_event)

        logger.info(
            f"Drift detection completed: drift={drift_result.drift_detected}, "
            f"retraining={drift_result.retraining_required} ({drift_severity})"
        )

        return drift_result

    def _determine_drift_severity(self, drift_result: DriftDetectionResult) -> str:
        """Determine drift severity based on detection results."""
        total_drift_features = len(drift_result.features_with_ks_drift) + len(
            drift_result.features_with_psi_drift
        )

        if drift_result.retraining_required:
            return "CRITICAL"
        if total_drift_features >= 3:
            return "HIGH"
        if total_drift_features >= 1:
            return "MEDIUM"
        return "LOW"

    async def _trigger_retraining_event(self, drift_event: DriftEvent):
        """Trigger model retraining event."""
        retraining_event = DriftEvent(
            event_type="retraining_required",
            timestamp=datetime.now().isoformat(),
            constitutional_hash=self.constitutional_hash,
            model_id=drift_event.model_id,
            service_id=drift_event.service_id,
            drift_detected=True,
            retraining_required=True,
            features_with_drift=drift_event.features_with_drift,
            drift_severity="CRITICAL",
            metadata={
                **drift_event.metadata,
                "retraining_trigger": "drift_detection",
                "priority": "HIGH",
            },
        )

        await self.publish_drift_event(retraining_event)

    async def start_streaming_drift_monitoring(
        self,
        data_stream: AsyncGenerator[pd.DataFrame, None],
        model_id: str,
        service_id: str = "acgs_service",
    ):
        """Start streaming drift monitoring for real-time data."""
        logger.info(f"🚀 Starting streaming drift monitoring for {model_id}")

        data_buffer = []

        async for data_batch in data_stream:
            try:
                # Add to buffer
                data_buffer.append(data_batch)

                # Check if we have enough data for drift detection
                total_records = sum(len(batch) for batch in data_buffer)

                if total_records >= self.monitoring_config["window_size"]:
                    # Combine buffered data
                    combined_data = pd.concat(data_buffer, ignore_index=True)

                    # Take the most recent window
                    current_window = combined_data.tail(
                        self.monitoring_config["window_size"]
                    )

                    # Perform drift detection
                    await self.detect_drift_async(current_window, model_id, service_id)

                    # Keep only recent data in buffer (sliding window)
                    buffer_size = self.monitoring_config["window_size"] // 2
                    if total_records > buffer_size:
                        # Keep most recent data
                        remaining_data = combined_data.tail(buffer_size)
                        data_buffer = [remaining_data]

            except Exception as e:
                logger.error(f"❌ Error in streaming drift monitoring: {e}")
                await asyncio.sleep(1)

    async def periodic_drift_monitoring(
        self,
        data_source: Callable[[], pd.DataFrame],
        model_id: str,
        service_id: str = "acgs_service",
    ):
        """Start periodic drift monitoring with configurable intervals."""
        logger.info(f"🚀 Starting periodic drift monitoring for {model_id}")

        while True:
            try:
                # Get current data
                current_data = data_source()

                if isinstance(current_data, pd.DataFrame) and not current_data.empty:
                    # Perform drift detection
                    await self.detect_drift_async(current_data, model_id, service_id)

                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_config["monitoring_interval"])

            except Exception as e:
                logger.error(f"❌ Error in periodic drift monitoring: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying


# Example event handlers
async def handle_drift_detected(event: DriftEvent):
    """Handle drift detection events."""
    logger.warning(f"🚨 DRIFT DETECTED: {event.model_id} in {event.service_id}")
    logger.warning(f"   Features with drift: {len(event.features_with_drift)}")
    logger.warning(f"   Severity: {event.drift_severity}")


async def handle_retraining_required(event: DriftEvent):
    """Handle model retraining requirement events."""
    logger.critical(f"🔄 RETRAINING REQUIRED: {event.model_id}")
    logger.critical(f"   Service: {event.service_id}")
    logger.critical(f"   Drift features: {event.features_with_drift}")

    # In production: trigger actual model retraining pipeline
    await simulate_model_retraining(event.model_id)


async def simulate_model_retraining(model_id: str):
    """Simulate model retraining process."""
    logger.info(f"⚙️ Starting model retraining for {model_id}...")
    await asyncio.sleep(2)  # Simulate retraining time
    logger.info(f"✅ Model retraining completed for {model_id}")


# Example usage and testing
async def demo_event_driven_drift_detection():
    """Demonstrate event-driven drift detection."""

    # Initialize drift detector
    drift_detector = EventDrivenDriftDetector()

    # Register event handlers
    drift_detector.register_event_handler("drift_detected", handle_drift_detected)
    drift_detector.register_event_handler(
        "retraining_required", handle_retraining_required
    )

    # Connect to NATS (optional)
    await drift_detector.connect_to_nats()

    # Generate reference dataset
    print("📊 Generating reference dataset...")
    reference_data = pd.DataFrame(
        {
            "feature1": np.random.normal(0, 1, 1000),
            "feature2": np.random.normal(0, 1, 1000),
            "feature3": np.random.exponential(1, 1000),
            "timestamp": pd.date_range(start="2025-01-01", periods=1000, freq="1H"),
        }
    )

    # Register reference dataset
    drift_detector.register_reference_dataset("acgs_ml_router_v8", reference_data)

    # Generate current data with drift
    print("\n🔍 Testing drift detection...")

    # No drift scenario
    no_drift_data = pd.DataFrame(
        {
            "feature1": np.random.normal(0, 1, 500),
            "feature2": np.random.normal(0, 1, 500),
            "feature3": np.random.exponential(1, 500),
            "timestamp": pd.date_range(start="2025-01-15", periods=500, freq="1H"),
        }
    )

    # High drift scenario
    high_drift_data = pd.DataFrame(
        {
            "feature1": np.random.normal(2, 1, 500),  # Mean shift
            "feature2": np.random.normal(0, 2, 500),  # Variance change
            "feature3": np.random.exponential(2, 500),  # Distribution change
            "timestamp": pd.date_range(start="2025-01-20", periods=500, freq="1H"),
        }
    )

    # Test no drift
    print("\n🔍 Testing no drift scenario...")
    await drift_detector.detect_drift_async(
        no_drift_data, "acgs_ml_router_v8", "test_service"
    )

    # Test high drift
    print("\n🔍 Testing high drift scenario...")
    await drift_detector.detect_drift_async(
        high_drift_data, "acgs_ml_router_v8", "test_service"
    )

    # Cleanup
    await drift_detector.disconnect_from_nats()
    print("\n✅ Event-driven drift detection demo completed")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_event_driven_drift_detection())
