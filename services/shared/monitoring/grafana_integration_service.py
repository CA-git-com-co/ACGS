"""
Grafana Integration Service for ACGS Predictive Analytics
Constitutional Hash: cdd01ef066bc6cf2

Provides integration between predictive analytics and Grafana dashboards including:
- Real-time data feeding to Grafana datasources
- Custom dashboard provisioning
- Alert integration with constitutional compliance
- ML model metrics exposition
"""

import asyncio
import contextlib
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import aiohttp
    import requests

    HTTP_AVAILABLE = True
except ImportError:
    logger.warning("HTTP libraries not available")
    HTTP_AVAILABLE = False

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("Prometheus client not available")
    PROMETHEUS_AVAILABLE = False


@dataclass
class GrafanaDataPoint:
    """Data point for Grafana time series."""

    timestamp: int  # Unix timestamp in milliseconds
    value: float
    tags: dict[str, str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def to_grafana_format(self) -> list:
        """Convert to Grafana data point format [value, timestamp]."""
        return [self.value, self.timestamp]


@dataclass
class GrafanaAnnotation:
    """Grafana annotation for events and alerts."""

    time: int  # Unix timestamp in milliseconds
    timeEnd: int | None = None
    title: str = ""
    text: str = ""
    tags: list[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


class GrafanaIntegrationService:
    """Service for integrating ACGS predictive analytics with Grafana."""

    def __init__(
        self,
        grafana_url: str = "http://grafana:3000",
        grafana_api_key: str | None = None,
    ):
        self.grafana_url = grafana_url
        self.grafana_api_key = grafana_api_key
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Data buffers for efficient batching
        self.data_buffers = {
            "constitutional_compliance": [],
            "performance_metrics": [],
            "security_events": [],
            "anomaly_scores": [],
            "prediction_accuracy": [],
        }

        # Annotations buffer
        self.annotations_buffer = []

        # Dashboard configurations
        self.dashboard_configs = {}

        # Background tasks
        self.data_sync_task = None
        self.annotation_sync_task = None

        logger.info(
            f"Grafana Integration Service initialized with constitutional hash {CONSTITUTIONAL_HASH}"
        )

    async def start(self):
        """Start the integration service."""
        try:
            # Initialize dashboard configurations
            await self._load_dashboard_configs()

            # Start background sync tasks
            self.data_sync_task = asyncio.create_task(self._data_sync_loop())
            self.annotation_sync_task = asyncio.create_task(
                self._annotation_sync_loop()
            )

            # Provision dashboards if API key available
            if self.grafana_api_key:
                await self._provision_dashboards()

            logger.info("Grafana Integration Service started successfully")

        except Exception as e:
            logger.exception(f"Failed to start Grafana Integration Service: {e}")
            raise

    async def stop(self):
        """Stop the integration service."""
        try:
            # Cancel background tasks
            if self.data_sync_task:
                self.data_sync_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self.data_sync_task

            if self.annotation_sync_task:
                self.annotation_sync_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self.annotation_sync_task

            # Flush remaining data
            await self._flush_all_buffers()

            logger.info("Grafana Integration Service stopped")

        except Exception as e:
            logger.exception(f"Error stopping Grafana Integration Service: {e}")

    async def add_constitutional_compliance_data(
        self,
        timestamp: datetime,
        compliance_rate: float,
        metadata: dict[str, Any] | None = None,
    ):
        """Add constitutional compliance data point."""
        if metadata is None:
            metadata = {}

        data_point = GrafanaDataPoint(
            timestamp=int(timestamp.timestamp() * 1000),
            value=compliance_rate,
            tags={
                "metric_type": "constitutional_compliance",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **metadata,
            },
        )

        self.data_buffers["constitutional_compliance"].append(data_point)

        # Add annotation for significant changes
        if self._is_significant_compliance_change(compliance_rate):
            await self.add_compliance_annotation(timestamp, compliance_rate)

    async def add_performance_data(
        self,
        timestamp: datetime,
        metric_name: str,
        value: float,
        metadata: dict[str, Any] | None = None,
    ):
        """Add performance metric data point."""
        if metadata is None:
            metadata = {}

        data_point = GrafanaDataPoint(
            timestamp=int(timestamp.timestamp() * 1000),
            value=value,
            tags={
                "metric_type": "performance",
                "metric_name": metric_name,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **metadata,
            },
        )

        self.data_buffers["performance_metrics"].append(data_point)

    async def add_anomaly_score(
        self,
        timestamp: datetime,
        metric_name: str,
        anomaly_score: float,
        is_anomaly: bool = False,
    ):
        """Add anomaly detection score."""
        data_point = GrafanaDataPoint(
            timestamp=int(timestamp.timestamp() * 1000),
            value=anomaly_score,
            tags={
                "metric_type": "anomaly_score",
                "metric_name": metric_name,
                "is_anomaly": str(is_anomaly).lower(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

        self.data_buffers["anomaly_scores"].append(data_point)

        # Add annotation for detected anomalies
        if is_anomaly:
            await self.add_anomaly_annotation(timestamp, metric_name, anomaly_score)

    async def add_prediction_accuracy(
        self,
        timestamp: datetime,
        metric_name: str,
        accuracy: float,
        model_type: str = "ml",
    ):
        """Add ML model prediction accuracy."""
        data_point = GrafanaDataPoint(
            timestamp=int(timestamp.timestamp() * 1000),
            value=accuracy,
            tags={
                "metric_type": "prediction_accuracy",
                "metric_name": metric_name,
                "model_type": model_type,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

        self.data_buffers["prediction_accuracy"].append(data_point)

    async def add_compliance_annotation(
        self, timestamp: datetime, compliance_rate: float
    ):
        """Add constitutional compliance annotation."""
        severity = (
            "critical"
            if compliance_rate < 0.85
            else "warning" if compliance_rate < 0.90 else "info"
        )

        annotation = GrafanaAnnotation(
            time=int(timestamp.timestamp() * 1000),
            title=f"Constitutional Compliance: {compliance_rate:.1%}",
            text=f"Compliance rate changed to {compliance_rate:.1%}. Constitutional hash: {CONSTITUTIONAL_HASH}",
            tags=[
                "constitutional_compliance",
                f"severity_{severity}",
                f"hash_{CONSTITUTIONAL_HASH}",
            ],
        )

        self.annotations_buffer.append(annotation)

    async def add_anomaly_annotation(
        self, timestamp: datetime, metric_name: str, anomaly_score: float
    ):
        """Add anomaly detection annotation."""
        severity = "critical" if anomaly_score > 0.9 else "warning"

        annotation = GrafanaAnnotation(
            time=int(timestamp.timestamp() * 1000),
            title=f"Anomaly Detected: {metric_name}",
            text=f"Anomaly score: {anomaly_score:.2%} for {metric_name}. Requires investigation.",
            tags=[
                "anomaly_detection",
                f"metric_{metric_name}",
                f"severity_{severity}",
                f"hash_{CONSTITUTIONAL_HASH}",
            ],
        )

        self.annotations_buffer.append(annotation)

    async def add_prediction_annotation(
        self,
        timestamp: datetime,
        metric_name: str,
        predicted_value: float,
        horizon_hours: int,
    ):
        """Add prediction annotation."""
        annotation = GrafanaAnnotation(
            time=int(timestamp.timestamp() * 1000),
            title=f"Prediction: {metric_name}",
            text=f"Predicted {metric_name}: {predicted_value:.2f} in {horizon_hours}h. Model-based forecast.",
            tags=[
                "prediction",
                f"metric_{metric_name}",
                f"horizon_{horizon_hours}h",
                f"hash_{CONSTITUTIONAL_HASH}",
            ],
        )

        self.annotations_buffer.append(annotation)

    def _is_significant_compliance_change(self, compliance_rate: float) -> bool:
        """Determine if compliance rate change is significant enough for annotation."""
        # Check recent compliance data
        recent_data = (
            self.data_buffers["constitutional_compliance"][-10:]
            if self.data_buffers["constitutional_compliance"]
            else []
        )

        if not recent_data:
            return True  # First data point

        recent_avg = sum(dp.value for dp in recent_data) / len(recent_data)
        change_threshold = 0.05  # 5% change threshold

        return abs(compliance_rate - recent_avg) > change_threshold

    async def _data_sync_loop(self):
        """Background loop for syncing data to Grafana."""
        while True:
            try:
                await asyncio.sleep(30)  # Sync every 30 seconds
                await self._flush_all_buffers()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in data sync loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _annotation_sync_loop(self):
        """Background loop for syncing annotations to Grafana."""
        while True:
            try:
                await asyncio.sleep(10)  # Sync annotations more frequently
                await self._flush_annotations()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in annotation sync loop: {e}")
                await asyncio.sleep(30)  # Wait on error

    async def _flush_all_buffers(self):
        """Flush all data buffers to Grafana."""
        if not HTTP_AVAILABLE:
            logger.debug("HTTP libraries not available, skipping buffer flush")
            return

        try:
            # Prepare data for Grafana
            grafana_data = self._prepare_grafana_data()

            if grafana_data:
                # Send to Grafana (would typically use Grafana's data source API)
                await self._send_to_grafana_datasource(grafana_data)

                # Clear buffers after successful send
                self._clear_data_buffers()

                logger.debug(f"Flushed {len(grafana_data)} data points to Grafana")

        except Exception as e:
            logger.exception(f"Failed to flush data buffers: {e}")

    async def _flush_annotations(self):
        """Flush annotations buffer to Grafana."""
        if not self.annotations_buffer or not HTTP_AVAILABLE:
            return

        try:
            # Send annotations to Grafana
            await self._send_annotations_to_grafana(self.annotations_buffer)

            # Clear buffer after successful send
            self.annotations_buffer.clear()

            logger.debug(
                f"Flushed {len(self.annotations_buffer)} annotations to Grafana"
            )

        except Exception as e:
            logger.exception(f"Failed to flush annotations: {e}")

    def _prepare_grafana_data(self) -> list[dict[str, Any]]:
        """Prepare data in Grafana-compatible format."""
        grafana_data = []

        for buffer_name, data_points in self.data_buffers.items():
            if not data_points:
                continue

            for dp in data_points:
                grafana_point = {
                    "target": f"acgs.{buffer_name}",
                    "datapoints": [dp.to_grafana_format()],
                    "tags": dp.tags,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }
                grafana_data.append(grafana_point)

        return grafana_data

    def _clear_data_buffers(self):
        """Clear all data buffers."""
        for buffer_name in self.data_buffers:
            self.data_buffers[buffer_name].clear()

    async def _send_to_grafana_datasource(self, data: list[dict[str, Any]]):
        """Send data to Grafana datasource."""
        if not HTTP_AVAILABLE:
            return

        # This would typically integrate with Grafana's SimpleJSON datasource
        # or a custom datasource plugin for real-time data

        headers = {
            "Content-Type": "application/json",
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
        }

        if self.grafana_api_key:
            headers["Authorization"] = f"Bearer {self.grafana_api_key}"

        # For demo purposes, we'll log the data
        # In production, this would POST to Grafana's datasource endpoint
        logger.debug(f"Would send to Grafana: {len(data)} data points")

    async def _send_annotations_to_grafana(self, annotations: list[GrafanaAnnotation]):
        """Send annotations to Grafana."""
        if not HTTP_AVAILABLE or not self.grafana_api_key:
            return

        for annotation in annotations:
            asdict(annotation)

            # For demo purposes, we'll log the annotation
            # In production, this would POST to Grafana's annotations API
            logger.debug(f"Would send annotation to Grafana: {annotation.title}")

    async def _load_dashboard_configs(self):
        """Load dashboard configurations."""
        self.dashboard_configs = {
            "predictive_analytics": {
                "uid": "acgs-predictive-analytics",
                "title": "ACGS Predictive Analytics Dashboard",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "refresh_interval": "30s",
                "panels": [
                    "constitutional_compliance_prediction",
                    "performance_latency_prediction",
                    "anomaly_detection_scores",
                    "ml_model_accuracy",
                ],
            },
            "constitutional_compliance": {
                "uid": "acgs-constitutional-compliance",
                "title": "Constitutional Compliance Monitoring",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "refresh_interval": "15s",
                "panels": [
                    "compliance_rate_current",
                    "compliance_trend",
                    "violation_alerts",
                    "constitutional_hash_validation",
                ],
            },
        }

    async def _provision_dashboards(self):
        """Provision dashboards in Grafana."""
        if not HTTP_AVAILABLE or not self.grafana_api_key:
            logger.warning(
                "Cannot provision dashboards: missing HTTP libraries or API key"
            )
            return

        try:

            for config in self.dashboard_configs.values():
                # This would typically create/update dashboards via Grafana API
                logger.info(f"Would provision dashboard: {config['title']}")

        except Exception as e:
            logger.exception(f"Failed to provision dashboards: {e}")

    async def get_dashboard_data_source_config(self) -> dict[str, Any]:
        """Get configuration for Grafana data source."""
        return {
            "name": "ACGS Predictive Analytics",
            "type": "simplejson",
            "url": "http://predictive-analytics:8090/grafana-datasource",
            "access": "proxy",
            "basicAuth": False,
            "isDefault": False,
            "jsonData": {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timeout": 30,
                "keepCookies": [],
            },
            "readOnly": False,
        }

    async def export_metrics_for_prometheus(self) -> str:
        """Export current metrics in Prometheus format."""
        if not PROMETHEUS_AVAILABLE:
            return ""

        try:
            # Create temporary registry for export
            registry = CollectorRegistry()

            # Add current buffer data as metrics
            # This would be implemented with proper Prometheus metrics

            return generate_latest(registry).decode("utf-8")

        except Exception as e:
            logger.exception(f"Failed to export Prometheus metrics: {e}")
            return ""

    def get_service_status(self) -> dict[str, Any]:
        """Get integration service status."""
        buffer_sizes = {name: len(buffer) for name, buffer in self.data_buffers.items()}

        return {
            "service": "grafana-integration",
            "status": "running",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "grafana_url": self.grafana_url,
            "api_key_configured": bool(self.grafana_api_key),
            "buffer_sizes": buffer_sizes,
            "annotations_buffered": len(self.annotations_buffer),
            "dashboard_configs": len(self.dashboard_configs),
            "last_sync": datetime.now(timezone.utc).isoformat(),
        }
