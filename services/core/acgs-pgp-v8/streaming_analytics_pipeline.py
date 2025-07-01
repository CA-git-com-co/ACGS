#!/usr/bin/env python3
"""
ACGS Streaming Analytics Pipeline

Real-time streaming data processing for ACGS platform using NATS Streaming:
- Windowed statistical analysis with configurable time windows
- Real-time data quality monitoring
- Continuous drift detection
- Constitutional compliance streaming validation
- Event-driven analytics with <100ms latency

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, asdict
from collections import deque
import warnings

warnings.filterwarnings("ignore")

# Import Phase 1 event-driven frameworks
from event_driven_data_quality import EventDrivenDataQualityFramework, QualityEvent
from event_driven_drift_detection import EventDrivenDriftDetector, DriftEvent
from nats_event_broker import NATSEventBroker, ACGSEvent

# NATS Streaming integration
try:
    import asyncio_nats_streaming as nats_streaming
    from asyncio_nats_streaming.aio.client import Client as STAN

    NATS_STREAMING_AVAILABLE = True
except ImportError:
    NATS_STREAMING_AVAILABLE = False
    print(
        "⚠️ NATS Streaming not available - install with: pip install asyncio-nats-streaming"
    )

logger = logging.getLogger(__name__)


@dataclass
class StreamingWindow:
    """Configurable time window for streaming analytics."""

    window_size_seconds: int
    slide_interval_seconds: int
    window_type: str  # 'tumbling', 'sliding', 'session'
    max_records: int = 10000


@dataclass
class StreamingMetrics:
    """Metrics for streaming analytics performance."""

    window_id: str
    timestamp: str
    records_processed: int
    processing_latency_ms: float
    quality_score: float
    drift_detected: bool
    compliance_score: float
    constitutional_hash: str


class StreamingAnalyticsPipeline:
    """Real-time streaming analytics pipeline for ACGS platform."""

    def __init__(
        self,
        nats_url: str = "nats://localhost:4222",
        cluster_id: str = "acgs-streaming-cluster",
        client_id: str = "acgs-analytics-pipeline",
    ):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.nats_url = nats_url
        self.cluster_id = cluster_id
        self.client_id = client_id
        self.stan_client: Optional[STAN] = None

        # Initialize Phase 1 frameworks
        self.quality_framework = EventDrivenDataQualityFramework(nats_url)
        self.drift_detector = EventDrivenDriftDetector(nats_url)
        self.event_broker = NATSEventBroker(nats_url)

        # Streaming configuration
        self.streaming_config = {
            "default_window": StreamingWindow(
                window_size_seconds=60,  # 1-minute windows
                slide_interval_seconds=10,  # 10-second slides
                window_type="sliding",
                max_records=1000,
            ),
            "quality_window": StreamingWindow(
                window_size_seconds=30,  # 30-second quality checks
                slide_interval_seconds=5,  # 5-second slides
                window_type="tumbling",
                max_records=500,
            ),
            "drift_window": StreamingWindow(
                window_size_seconds=300,  # 5-minute drift analysis
                slide_interval_seconds=60,  # 1-minute slides
                window_type="sliding",
                max_records=2000,
            ),
        }

        # Data buffers for windowed analysis
        self.data_buffers: Dict[str, deque] = {
            "quality": deque(maxlen=10000),
            "drift": deque(maxlen=20000),
            "performance": deque(maxlen=5000),
            "compliance": deque(maxlen=5000),
        }

        # Window managers
        self.active_windows: Dict[str, Dict] = {}

        logger.info(f"Streaming Analytics Pipeline initialized")
        logger.info(f"Constitutional hash: {self.constitutional_hash}")
        logger.info(f"NATS Streaming URL: {self.nats_url}")

    async def connect_to_streaming(self) -> bool:
        """Connect to NATS Streaming server."""
        if not NATS_STREAMING_AVAILABLE:
            logger.warning("NATS Streaming not available - using mock mode")
            return False

        try:
            self.stan_client = await nats_streaming.connect(
                cluster_id=self.cluster_id,
                client_id=self.client_id,
                nats_url=self.nats_url,
            )

            logger.info(f"✅ Connected to NATS Streaming cluster: {self.cluster_id}")

            # Connect Phase 1 frameworks
            await self.quality_framework.connect_to_nats()
            await self.drift_detector.connect_to_nats()
            await self.event_broker.connect()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS Streaming: {e}")
            return False

    async def disconnect_from_streaming(self):
        """Disconnect from NATS Streaming server."""
        if self.stan_client:
            await self.stan_client.close()
            logger.info("Disconnected from NATS Streaming")

        # Disconnect Phase 1 frameworks
        await self.quality_framework.disconnect_from_nats()
        await self.drift_detector.disconnect_from_nats()
        await self.event_broker.disconnect()

    async def create_windowed_stream(
        self, subject: str, window_config: StreamingWindow, processor: Callable
    ) -> AsyncGenerator[pd.DataFrame, None]:
        """Create windowed data stream for analytics."""

        window_buffer = deque(maxlen=window_config.max_records)
        last_window_time = datetime.now()

        async def message_handler(msg):
            try:
                # Parse incoming data
                data = json.loads(msg.data.decode())

                # Add timestamp if not present
                if "timestamp" not in data:
                    data["timestamp"] = datetime.now().isoformat()

                # Add to window buffer
                window_buffer.append(data)

                # Check if window should be processed
                current_time = datetime.now()
                time_since_last = (current_time - last_window_time).total_seconds()

                if (
                    time_since_last >= window_config.slide_interval_seconds
                    or len(window_buffer) >= window_config.max_records
                ):

                    # Create DataFrame from window data
                    if window_buffer:
                        window_df = pd.DataFrame(list(window_buffer))

                        # Process window
                        await processor(window_df, window_config)

                        # Update last window time
                        nonlocal last_window_time
                        last_window_time = current_time

                        # Clear buffer for tumbling windows
                        if window_config.window_type == "tumbling":
                            window_buffer.clear()

                        yield window_df

            except Exception as e:
                logger.error(f"❌ Error processing streaming message: {e}")

        # Subscribe to streaming subject
        if self.stan_client:
            await self.stan_client.subscribe(
                subject=subject,
                cb=message_handler,
                durable_name=f"acgs-{subject.replace('.', '-')}-durable",
            )

    async def process_quality_stream(
        self, window_df: pd.DataFrame, window_config: StreamingWindow
    ):
        """Process streaming data quality analysis."""
        start_time = datetime.now()

        try:
            # Perform quality assessment on window
            quality_metrics = await self.quality_framework.assess_quality_async(
                df=window_df,
                service_id="streaming_analytics",
                target_column=None,
                timestamp_column="timestamp",
            )

            # Calculate processing latency
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            # Create streaming metrics
            streaming_metrics = StreamingMetrics(
                window_id=f"quality-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                timestamp=datetime.now().isoformat(),
                records_processed=len(window_df),
                processing_latency_ms=processing_time,
                quality_score=quality_metrics.overall_score,
                drift_detected=False,  # Will be updated by drift processor
                compliance_score=1.0,  # Will be updated by compliance processor
                constitutional_hash=self.constitutional_hash,
            )

            # Publish streaming metrics
            await self._publish_streaming_metrics(streaming_metrics)

            logger.info(
                f"📊 Quality window processed: {len(window_df)} records, "
                f"score: {quality_metrics.overall_score:.3f}, "
                f"latency: {processing_time:.1f}ms"
            )

        except Exception as e:
            logger.error(f"❌ Error processing quality stream: {e}")

    async def process_drift_stream(
        self, window_df: pd.DataFrame, window_config: StreamingWindow
    ):
        """Process streaming drift detection analysis."""
        start_time = datetime.now()

        try:
            # Check if we have reference data for drift detection
            model_id = "acgs_streaming_model"

            if model_id not in self.drift_detector.reference_datasets:
                # Use first window as reference (in production, use trained reference)
                self.drift_detector.register_reference_dataset(model_id, window_df)
                logger.info(f"Registered reference dataset for {model_id}")
                return

            # Perform drift detection on window
            drift_result = await self.drift_detector.detect_drift_async(
                current_data=window_df,
                model_id=model_id,
                service_id="streaming_analytics",
            )

            # Calculate processing latency
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(
                f"🔄 Drift window processed: {len(window_df)} records, "
                f"drift: {drift_result.drift_detected}, "
                f"retraining: {drift_result.retraining_required}, "
                f"latency: {processing_time:.1f}ms"
            )

        except Exception as e:
            logger.error(f"❌ Error processing drift stream: {e}")

    async def process_performance_stream(
        self, window_df: pd.DataFrame, window_config: StreamingWindow
    ):
        """Process streaming performance analysis."""
        start_time = datetime.now()

        try:
            # Calculate performance metrics for the window
            if "response_time_ms" in window_df.columns:
                avg_response_time = window_df["response_time_ms"].mean()
                p95_response_time = window_df["response_time_ms"].quantile(0.95)

                # Check performance thresholds
                if avg_response_time > 500:  # 500ms threshold
                    await self._publish_performance_alert(window_df, avg_response_time)

            # Calculate processing latency
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(
                f"⚡ Performance window processed: {len(window_df)} records, "
                f"latency: {processing_time:.1f}ms"
            )

        except Exception as e:
            logger.error(f"❌ Error processing performance stream: {e}")

    async def _publish_streaming_metrics(self, metrics: StreamingMetrics):
        """Publish streaming analytics metrics."""
        event = ACGSEvent(
            event_type="streaming_metrics",
            timestamp=datetime.now().isoformat(),
            constitutional_hash=self.constitutional_hash,
            source_service="streaming_analytics",
            target_service=None,
            event_id=metrics.window_id,
            payload=asdict(metrics),
            priority="NORMAL",
        )

        await self.event_broker.publish_event("acgs.streaming.metrics", event)

    async def _publish_performance_alert(
        self, window_df: pd.DataFrame, avg_response_time: float
    ):
        """Publish performance alert for slow response times."""
        alert_event = ACGSEvent(
            event_type="performance_alert",
            timestamp=datetime.now().isoformat(),
            constitutional_hash=self.constitutional_hash,
            source_service="streaming_analytics",
            target_service="performance_monitor",
            event_id=f"perf-alert-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            payload={
                "metric": "response_time",
                "value": avg_response_time,
                "threshold": 500,
                "window_size": len(window_df),
                "severity": "HIGH" if avg_response_time > 1000 else "MEDIUM",
            },
            priority="HIGH",
        )

        await self.event_broker.publish_event(
            "acgs.performance.alert.high", alert_event
        )

    async def start_streaming_analytics(self):
        """Start the streaming analytics pipeline."""
        logger.info("🚀 Starting streaming analytics pipeline...")

        # Start quality stream processing
        quality_stream = self.create_windowed_stream(
            subject="acgs.data.quality",
            window_config=self.streaming_config["quality_window"],
            processor=self.process_quality_stream,
        )

        # Start drift stream processing
        drift_stream = self.create_windowed_stream(
            subject="acgs.data.drift",
            window_config=self.streaming_config["drift_window"],
            processor=self.process_drift_stream,
        )

        # Start performance stream processing
        performance_stream = self.create_windowed_stream(
            subject="acgs.data.performance",
            window_config=self.streaming_config["default_window"],
            processor=self.process_performance_stream,
        )

        # Run all streams concurrently
        await asyncio.gather(
            self._consume_stream(quality_stream),
            self._consume_stream(drift_stream),
            self._consume_stream(performance_stream),
        )

    async def _consume_stream(self, stream: AsyncGenerator):
        """Consume data from a stream."""
        try:
            async for window_data in stream:
                # Stream processing happens in the processor callbacks
                pass
        except Exception as e:
            logger.error(f"❌ Error consuming stream: {e}")


# Example usage and testing
async def demo_streaming_analytics():
    """Demonstrate streaming analytics pipeline."""

    # Initialize streaming pipeline
    pipeline = StreamingAnalyticsPipeline()

    # Connect to streaming
    if not await pipeline.connect_to_streaming():
        logger.error("❌ Failed to connect to streaming - using mock mode")

    # Generate sample streaming data
    async def generate_sample_data():
        """Generate sample streaming data for testing."""
        for i in range(100):
            # Generate sample data point
            data_point = {
                "timestamp": datetime.now().isoformat(),
                "service_id": f"service_{i % 7}",
                "response_time_ms": np.random.lognormal(6, 0.5),
                "quality_score": np.random.beta(8, 2),
                "feature1": np.random.normal(0, 1),
                "feature2": np.random.normal(0, 1),
                "constitutional_hash": pipeline.constitutional_hash,
            }

            # Publish to streaming subjects
            if pipeline.stan_client:
                await pipeline.stan_client.publish(
                    "acgs.data.quality", json.dumps(data_point).encode()
                )
                await pipeline.stan_client.publish(
                    "acgs.data.performance", json.dumps(data_point).encode()
                )

            # Simulate real-time data arrival
            await asyncio.sleep(0.1)

    # Start data generation and streaming analytics
    await asyncio.gather(generate_sample_data(), pipeline.start_streaming_analytics())

    # Cleanup
    await pipeline.disconnect_from_streaming()
    print("✅ Streaming analytics demo completed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run demo
    asyncio.run(demo_streaming_analytics())
