#!/usr/bin/env python3
"""
Streaming Data Converter for ACGS-PGP v8

Converts existing batch-oriented analysis components to support real-time data streams:
- Adapts data_quality_framework.py for streaming analysis
- Converts data_drift_detection.py for continuous monitoring
- Provides streaming wrappers for existing statistical methods
- Maintains constitutional compliance in streaming context

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import warnings
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Import existing batch components
from baseline_performance_measurement import BaselinePerformanceMeasurement
from data_drift_detection import DataDriftDetector, DriftDetectionResult
from data_quality_framework import DataQualityAssessment, DataQualityMetrics

logger = logging.getLogger(__name__)


@dataclass
class StreamingBuffer:
    """Buffer for streaming data with configurable retention."""

    max_size: int
    retention_seconds: int
    data: deque
    timestamps: deque

    def __post_init__(self):
        self.data = deque(maxlen=self.max_size)
        self.timestamps = deque(maxlen=self.max_size)

    def add_record(self, record: dict[str, Any]):
        """Add a record to the streaming buffer."""
        current_time = datetime.now()
        self.data.append(record)
        self.timestamps.append(current_time)

        # Clean old records based on retention policy
        self._clean_old_records()

    def _clean_old_records(self):
        """Remove records older than retention period."""
        cutoff_time = datetime.now() - timedelta(seconds=self.retention_seconds)

        while self.timestamps and self.timestamps[0] < cutoff_time:
            self.data.popleft()
            self.timestamps.popleft()

    def get_dataframe(self) -> pd.DataFrame:
        """Convert buffer contents to DataFrame."""
        if not self.data:
            return pd.DataFrame()

        df = pd.DataFrame(list(self.data))
        df["buffer_timestamp"] = list(self.timestamps)
        return df

    def size(self) -> int:
        """Get current buffer size."""
        return len(self.data)


class StreamingDataQualityAdapter:
    """Adapter to make batch data quality framework work with streaming data."""

    def __init__(self, buffer_size: int = 1000, retention_seconds: int = 3600):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.batch_assessor = DataQualityAssessment()
        self.streaming_buffer = StreamingBuffer(buffer_size, retention_seconds)

        # Streaming-specific configuration
        self.streaming_config = {
            "min_records_for_assessment": 50,
            "assessment_interval_seconds": 30,
            "quality_threshold": 0.8,
            "alert_cooldown_seconds": 300,
        }

        self.last_assessment_time = datetime.min
        self.last_alert_time = datetime.min

        logger.info("Streaming Data Quality Adapter initialized")

    async def process_streaming_record(
        self, record: dict[str, Any]
    ) -> DataQualityMetrics | None:
        """Process a single streaming record and potentially trigger assessment."""

        # Add record to buffer
        self.streaming_buffer.add_record(record)

        # Check if assessment should be triggered
        current_time = datetime.now()
        time_since_last = (current_time - self.last_assessment_time).total_seconds()

        if (
            time_since_last >= self.streaming_config["assessment_interval_seconds"]
            and self.streaming_buffer.size()
            >= self.streaming_config["min_records_for_assessment"]
        ):
            # Perform quality assessment on buffered data
            return await self._assess_buffer_quality()

        return None

    async def _assess_buffer_quality(self) -> DataQualityMetrics:
        """Assess quality of data in the streaming buffer."""

        # Get DataFrame from buffer
        df = self.streaming_buffer.get_dataframe()

        if df.empty:
            logger.warning("⚠️ Empty buffer for quality assessment")
            return None

        # Perform batch assessment on streaming data
        metrics = await asyncio.get_event_loop().run_in_executor(
            None, self.batch_assessor.comprehensive_assessment, df
        )

        # Update last assessment time
        self.last_assessment_time = datetime.now()

        # Check for quality alerts
        if metrics.overall_score < self.streaming_config["quality_threshold"]:
            await self._handle_quality_alert(metrics)

        logger.info(
            f"📊 Streaming quality assessment: {metrics.overall_score:.3f} "
            f"({self.streaming_buffer.size()} records)"
        )

        return metrics

    async def _handle_quality_alert(self, metrics: DataQualityMetrics):
        """Handle quality alert with cooldown to prevent spam."""
        current_time = datetime.now()
        time_since_last_alert = (current_time - self.last_alert_time).total_seconds()

        if time_since_last_alert >= self.streaming_config["alert_cooldown_seconds"]:
            logger.warning(
                f"🚨 STREAMING QUALITY ALERT: Score {metrics.overall_score:.3f}"
            )
            self.last_alert_time = current_time

            # In production: publish alert event
            # await self.publish_quality_alert(metrics)


class StreamingDriftAdapter:
    """Adapter to make batch drift detection work with streaming data."""

    def __init__(self, buffer_size: int = 2000, retention_seconds: int = 7200):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.batch_detector = DataDriftDetector()
        self.reference_buffer = StreamingBuffer(buffer_size, retention_seconds)
        self.current_buffer = StreamingBuffer(buffer_size // 2, retention_seconds // 2)

        # Streaming-specific configuration
        self.streaming_config = {
            "min_records_for_detection": 100,
            "detection_interval_seconds": 300,  # 5 minutes
            "reference_update_interval_seconds": 3600,  # 1 hour
            "drift_threshold": 0.05,
        }

        self.last_detection_time = datetime.min
        self.last_reference_update = datetime.min
        self.reference_established = False

        logger.info("Streaming Drift Adapter initialized")

    async def process_streaming_record(
        self, record: dict[str, Any]
    ) -> DriftDetectionResult | None:
        """Process a single streaming record for drift detection."""

        # Add record to current buffer
        self.current_buffer.add_record(record)

        # If reference not established, build reference dataset
        if not self.reference_established:
            self.reference_buffer.add_record(record)

            if (
                self.reference_buffer.size()
                >= self.streaming_config["min_records_for_detection"]
            ):
                self.reference_established = True
                logger.info(
                    f"✅ Reference dataset established with {self.reference_buffer.size()} records"
                )

            return None

        # Check if drift detection should be triggered
        current_time = datetime.now()
        time_since_last = (current_time - self.last_detection_time).total_seconds()

        if (
            time_since_last >= self.streaming_config["detection_interval_seconds"]
            and self.current_buffer.size()
            >= self.streaming_config["min_records_for_detection"]
        ):
            # Perform drift detection
            return await self._detect_streaming_drift()

        return None

    async def _detect_streaming_drift(self) -> DriftDetectionResult:
        """Detect drift between reference and current streaming data."""

        # Get DataFrames from buffers
        reference_df = self.reference_buffer.get_dataframe()
        current_df = self.current_buffer.get_dataframe()

        if reference_df.empty or current_df.empty:
            logger.warning("⚠️ Empty buffers for drift detection")
            return None

        # Remove timestamp columns for drift analysis
        reference_clean = reference_df.drop(
            columns=["buffer_timestamp"], errors="ignore"
        )
        current_clean = current_df.drop(columns=["buffer_timestamp"], errors="ignore")

        # Perform batch drift detection on streaming data
        drift_result = await asyncio.get_event_loop().run_in_executor(
            None,
            self.batch_detector.comprehensive_drift_analysis,
            reference_clean,
            current_clean,
        )

        # Update last detection time
        self.last_detection_time = datetime.now()

        # Check if reference should be updated (concept drift adaptation)
        await self._maybe_update_reference()

        logger.info(
            f"🔄 Streaming drift detection: drift={drift_result.drift_detected}, "
            f"retraining={drift_result.retraining_required}"
        )

        return drift_result

    async def _maybe_update_reference(self):
        """Update reference dataset periodically for concept drift adaptation."""
        current_time = datetime.now()
        time_since_update = (current_time - self.last_reference_update).total_seconds()

        if (
            time_since_update
            >= self.streaming_config["reference_update_interval_seconds"]
        ):
            # Move current data to reference (sliding reference window)
            current_df = self.current_buffer.get_dataframe()

            if not current_df.empty:
                # Add current data to reference buffer
                for _, record in current_df.iterrows():
                    record_dict = record.to_dict()
                    self.reference_buffer.add_record(record_dict)

                # Clear current buffer
                self.current_buffer = StreamingBuffer(
                    self.current_buffer.max_size, self.current_buffer.retention_seconds
                )

                self.last_reference_update = current_time
                logger.info("🔄 Reference dataset updated with streaming data")


class StreamingPerformanceAdapter:
    """Adapter to make batch performance measurement work with streaming data."""

    def __init__(self, buffer_size: int = 500, retention_seconds: int = 1800):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.batch_analyzer = BaselinePerformanceMeasurement()
        self.performance_buffer = StreamingBuffer(buffer_size, retention_seconds)

        # Streaming-specific configuration
        self.streaming_config = {
            "min_records_for_analysis": 20,
            "analysis_interval_seconds": 60,  # 1 minute
            "response_time_threshold_ms": 500,
            "error_rate_threshold": 0.05,
        }

        self.last_analysis_time = datetime.min

        logger.info("Streaming Performance Adapter initialized")

    async def process_streaming_record(
        self, record: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Process a single streaming performance record."""

        # Add record to buffer
        self.performance_buffer.add_record(record)

        # Check if analysis should be triggered
        current_time = datetime.now()
        time_since_last = (current_time - self.last_analysis_time).total_seconds()

        if (
            time_since_last >= self.streaming_config["analysis_interval_seconds"]
            and self.performance_buffer.size()
            >= self.streaming_config["min_records_for_analysis"]
        ):
            # Perform performance analysis
            return await self._analyze_streaming_performance()

        return None

    async def _analyze_streaming_performance(self) -> dict[str, Any]:
        """Analyze performance of streaming data."""

        # Get DataFrame from buffer
        df = self.performance_buffer.get_dataframe()

        if df.empty:
            logger.warning("⚠️ Empty buffer for performance analysis")
            return None

        # Calculate streaming performance metrics
        metrics = {}

        if "response_time_ms" in df.columns:
            metrics["avg_response_time_ms"] = df["response_time_ms"].mean()
            metrics["p95_response_time_ms"] = df["response_time_ms"].quantile(0.95)
            metrics["p99_response_time_ms"] = df["response_time_ms"].quantile(0.99)

        if "error_rate" in df.columns:
            metrics["avg_error_rate"] = df["error_rate"].mean()

        if "throughput_rps" in df.columns:
            metrics["avg_throughput_rps"] = df["throughput_rps"].mean()

        # Add metadata
        metrics.update(
            {
                "records_analyzed": len(df),
                "analysis_timestamp": datetime.now().isoformat(),
                "constitutional_hash": self.constitutional_hash,
            }
        )

        # Update last analysis time
        self.last_analysis_time = datetime.now()

        # Check for performance alerts
        await self._check_performance_alerts(metrics)

        logger.info(
            f"⚡ Streaming performance analysis: "
            f"avg_rt={metrics.get('avg_response_time_ms', 0):.1f}ms, "
            f"records={metrics['records_analyzed']}"
        )

        return metrics

    async def _check_performance_alerts(self, metrics: dict[str, Any]):
        """Check for performance threshold violations."""

        # Check response time threshold
        if "avg_response_time_ms" in metrics:
            if (
                metrics["avg_response_time_ms"]
                > self.streaming_config["response_time_threshold_ms"]
            ):
                logger.warning(
                    f"🚨 STREAMING PERFORMANCE ALERT: "
                    f"Response time {metrics['avg_response_time_ms']:.1f}ms "
                    f"exceeds threshold {self.streaming_config['response_time_threshold_ms']}ms"
                )

        # Check error rate threshold
        if "avg_error_rate" in metrics:
            if (
                metrics["avg_error_rate"]
                > self.streaming_config["error_rate_threshold"]
            ):
                logger.warning(
                    f"🚨 STREAMING ERROR RATE ALERT: "
                    f"Error rate {metrics['avg_error_rate']:.3f} "
                    f"exceeds threshold {self.streaming_config['error_rate_threshold']}"
                )


class StreamingAnalyticsOrchestrator:
    """Orchestrates all streaming analytics adapters."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Initialize adapters
        self.quality_adapter = StreamingDataQualityAdapter()
        self.drift_adapter = StreamingDriftAdapter()
        self.performance_adapter = StreamingPerformanceAdapter()

        logger.info("Streaming Analytics Orchestrator initialized")

    async def process_streaming_data(self, data_stream: list[dict[str, Any]]):
        """Process streaming data through all adapters."""

        for record in data_stream:
            # Validate constitutional hash
            if "constitutional_hash" in record:
                if record["constitutional_hash"] != self.constitutional_hash:
                    logger.warning("⚠️ Constitutional hash mismatch in streaming record")
                    continue

            # Process through all adapters concurrently
            await asyncio.gather(
                self.quality_adapter.process_streaming_record(record),
                self.drift_adapter.process_streaming_record(record),
                self.performance_adapter.process_streaming_record(record),
                return_exceptions=True,
            )


# Example usage and testing
async def demo_streaming_conversion():
    """Demonstrate streaming data conversion."""

    # Initialize orchestrator
    orchestrator = StreamingAnalyticsOrchestrator()

    # Generate sample streaming data
    streaming_data = []
    for i in range(200):
        record = {
            "timestamp": datetime.now().isoformat(),
            "service_id": f"service_{i % 7}",
            "response_time_ms": np.random.lognormal(6, 0.5),
            "error_rate": np.random.exponential(0.02),
            "throughput_rps": np.random.normal(100, 20),
            "feature1": np.random.normal(0, 1),
            "feature2": np.random.normal(0, 1),
            "constitutional_hash": orchestrator.constitutional_hash,
        }
        streaming_data.append(record)

    # Process streaming data
    print("📊 Processing streaming data through adapters...")
    await orchestrator.process_streaming_data(streaming_data)

    print("✅ Streaming data conversion demo completed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run demo
    asyncio.run(demo_streaming_conversion())
