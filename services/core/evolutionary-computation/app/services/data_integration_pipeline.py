"""
Data Integration Pipeline for EC Service

Provides real-time data integration between the evolutionary computation service
and other ACGS-PGP services (gs-service, pgc-service, ac-service) for WINA optimization.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import httpx

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Types of data sources for integration."""

    GOVERNANCE_SYNTHESIS = "gs_service"
    POLICY_COMPLIANCE = "pgc_service"
    CONSTITUTIONAL_AI = "ac_service"
    SYSTEM_METRICS = "system_metrics"


@dataclass
class DataPoint:
    """Individual data point from integration pipeline."""

    source: DataSourceType
    timestamp: datetime
    data_type: str
    value: Any
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationMetrics:
    """Metrics for data integration performance."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)


class DataIntegrationPipeline:
    """
    Real-time data integration pipeline for EC service.

    Collects performance and compliance data from other ACGS services
    to provide WINA optimization with real-time system insights.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize data integration pipeline.

        Args:
            config: Integration configuration
        """
        self.config = config
        self.service_endpoints = config.get("service_endpoints", {})
        self.update_frequency = config.get("data_pipeline", {}).get(
            "update_frequency_seconds", 30
        )
        self.buffer_size = config.get("data_pipeline", {}).get("buffer_size", 1000)
        self.batch_size = config.get("data_pipeline", {}).get("batch_size", 100)

        # Data storage
        self.data_buffer: list[DataPoint] = []
        self.integration_metrics: dict[DataSourceType, IntegrationMetrics] = {
            source: IntegrationMetrics() for source in DataSourceType
        }

        # HTTP client for service communication
        self.http_client = httpx.AsyncClient(timeout=10.0)

        # Pipeline state
        self.pipeline_active = False
        self.last_collection_time = None

        logger.info("Data Integration Pipeline initialized")

    async def start_pipeline(self):
        """Start the data integration pipeline."""
        if self.pipeline_active:
            logger.warning("Pipeline already active")
            return

        self.pipeline_active = True
        logger.info("Starting data integration pipeline")

        # Start background collection tasks
        collection_task = asyncio.create_task(self._collection_loop())
        processing_task = asyncio.create_task(self._processing_loop())

        try:
            await asyncio.gather(collection_task, processing_task)
        except asyncio.CancelledError:
            logger.info("Pipeline tasks cancelled")
        except Exception as e:
            logger.exception(f"Pipeline error: {e}")
        finally:
            self.pipeline_active = False

    async def stop_pipeline(self):
        """Stop the data integration pipeline."""
        self.pipeline_active = False
        await self.http_client.aclose()
        logger.info("Data integration pipeline stopped")

    async def _collection_loop(self):
        """Main data collection loop."""
        while self.pipeline_active:
            try:
                start_time = time.time()

                # Collect data from all sources
                collection_tasks = [
                    self._collect_from_gs_service(),
                    self._collect_from_pgc_service(),
                    self._collect_from_ac_service(),
                    self._collect_system_metrics(),
                ]

                results = await asyncio.gather(
                    *collection_tasks, return_exceptions=True
                )

                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        source = list(DataSourceType)[i]
                        logger.warning(
                            f"Collection failed for {source.value}: {result}"
                        )

                collection_time = (time.time() - start_time) * 1000
                self.last_collection_time = datetime.now()

                logger.debug(f"Data collection completed in {collection_time:.1f}ms")

                # Wait for next collection cycle
                await asyncio.sleep(self.update_frequency)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Collection loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def _processing_loop(self):
        """Data processing and cleanup loop."""
        while self.pipeline_active:
            try:
                # Process buffered data
                if len(self.data_buffer) >= self.batch_size:
                    await self._process_data_batch()

                # Cleanup old data
                await self._cleanup_old_data()

                # Wait before next processing cycle
                await asyncio.sleep(10)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Processing loop error: {e}")
                await asyncio.sleep(5)

    async def _collect_from_gs_service(self):
        """Collect data from governance synthesis service."""
        try:
            gs_url = self.service_endpoints.get("gs_service", "http://localhost:8004")

            # Get synthesis performance metrics
            response = await self.http_client.get(f"{gs_url}/api/v1/info")
            if response.status_code == 200:
                data = response.json()

                data_point = DataPoint(
                    source=DataSourceType.GOVERNANCE_SYNTHESIS,
                    timestamp=datetime.now(),
                    data_type="service_info",
                    value=data,
                    metadata={"endpoint": "/api/v1/info"},
                )

                self.data_buffer.append(data_point)
                self._update_metrics(
                    DataSourceType.GOVERNANCE_SYNTHESIS,
                    True,
                    response.elapsed.total_seconds() * 1000,
                )

        except Exception as e:
            self._update_metrics(DataSourceType.GOVERNANCE_SYNTHESIS, False, 0)
            logger.warning(f"GS service collection failed: {e}")

    async def _collect_from_pgc_service(self):
        """Collect data from policy governance compliance service."""
        try:
            pgc_url = self.service_endpoints.get("pgc_service", "http://localhost:8005")

            # Get compliance metrics
            response = await self.http_client.get(f"{pgc_url}/health")
            if response.status_code == 200:
                data = response.json()

                data_point = DataPoint(
                    source=DataSourceType.POLICY_COMPLIANCE,
                    timestamp=datetime.now(),
                    data_type="health_status",
                    value=data,
                    metadata={"endpoint": "/health"},
                )

                self.data_buffer.append(data_point)
                self._update_metrics(
                    DataSourceType.POLICY_COMPLIANCE,
                    True,
                    response.elapsed.total_seconds() * 1000,
                )

        except Exception as e:
            self._update_metrics(DataSourceType.POLICY_COMPLIANCE, False, 0)
            logger.warning(f"PGC service collection failed: {e}")

    async def _collect_from_ac_service(self):
        """Collect data from constitutional AI service."""
        try:
            ac_url = self.service_endpoints.get("ac_service", "http://localhost:8001")

            # Get constitutional compliance data
            response = await self.http_client.get(f"{ac_url}/health")
            if response.status_code == 200:
                data = response.json()

                data_point = DataPoint(
                    source=DataSourceType.CONSTITUTIONAL_AI,
                    timestamp=datetime.now(),
                    data_type="constitutional_status",
                    value=data,
                    metadata={"endpoint": "/health"},
                )

                self.data_buffer.append(data_point)
                self._update_metrics(
                    DataSourceType.CONSTITUTIONAL_AI,
                    True,
                    response.elapsed.total_seconds() * 1000,
                )

        except Exception as e:
            self._update_metrics(DataSourceType.CONSTITUTIONAL_AI, False, 0)
            logger.warning(f"AC service collection failed: {e}")

    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            import psutil

            # Collect system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            system_data = {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "timestamp": datetime.now().isoformat(),
            }

            data_point = DataPoint(
                source=DataSourceType.SYSTEM_METRICS,
                timestamp=datetime.now(),
                data_type="system_performance",
                value=system_data,
                metadata={"collection_method": "psutil"},
            )

            self.data_buffer.append(data_point)
            self._update_metrics(
                DataSourceType.SYSTEM_METRICS, True, 10.0
            )  # Assume 10ms collection time

        except Exception as e:
            self._update_metrics(DataSourceType.SYSTEM_METRICS, False, 0)
            logger.warning(f"System metrics collection failed: {e}")

    async def _process_data_batch(self):
        """Process a batch of collected data."""
        try:
            if not self.data_buffer:
                return

            # Take a batch from the buffer
            batch = self.data_buffer[: self.batch_size]
            self.data_buffer = self.data_buffer[self.batch_size :]

            # Group data by source for processing
            grouped_data = {}
            for data_point in batch:
                source = data_point.source
                if source not in grouped_data:
                    grouped_data[source] = []
                grouped_data[source].append(data_point)

            # Process each source's data
            for source, data_points in grouped_data.items():
                await self._process_source_data(source, data_points)

            logger.debug(f"Processed batch of {len(batch)} data points")

        except Exception as e:
            logger.exception(f"Data batch processing failed: {e}")

    async def _process_source_data(
        self, source: DataSourceType, data_points: list[DataPoint]
    ):
        """Process data points from a specific source."""
        try:
            # Extract relevant metrics for WINA optimization
            if source == DataSourceType.GOVERNANCE_SYNTHESIS:
                # Process governance synthesis performance data
                for point in data_points:
                    if point.data_type == "service_info":
                        # Extract synthesis performance metrics
                        pass

            elif source == DataSourceType.POLICY_COMPLIANCE:
                # Process compliance metrics
                for point in data_points:
                    if point.data_type == "health_status":
                        # Extract compliance scores
                        pass

            elif source == DataSourceType.CONSTITUTIONAL_AI:
                # Process constitutional AI metrics
                for point in data_points:
                    if point.data_type == "constitutional_status":
                        # Extract constitutional compliance data
                        pass

            elif source == DataSourceType.SYSTEM_METRICS:
                # Process system performance metrics
                for point in data_points:
                    if point.data_type == "system_performance":
                        # Extract system performance data for optimization
                        pass

        except Exception as e:
            logger.exception(f"Source data processing failed for {source.value}: {e}")

    def _update_metrics(self, source: DataSourceType, success: bool, latency_ms: float):
        """Update integration metrics for a data source."""
        try:
            metrics = self.integration_metrics[source]
            metrics.total_requests += 1

            if success:
                metrics.successful_requests += 1
                # Update average latency with exponential moving average
                alpha = 0.1
                metrics.average_latency_ms = (
                    1 - alpha
                ) * metrics.average_latency_ms + alpha * latency_ms
            else:
                metrics.failed_requests += 1

            metrics.last_update = datetime.now()

        except Exception as e:
            logger.exception(f"Metrics update failed for {source.value}: {e}")

    async def _cleanup_old_data(self):
        """Remove old data points from buffer."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)  # Keep 1 hour of data

            self.data_buffer = [
                point for point in self.data_buffer if point.timestamp >= cutoff_time
            ]

        except Exception as e:
            logger.exception(f"Data cleanup failed: {e}")

    def get_integration_summary(self) -> dict[str, Any]:
        """Get summary of data integration performance."""
        try:
            summary = {
                "pipeline_active": self.pipeline_active,
                "last_collection": (
                    self.last_collection_time.isoformat()
                    if self.last_collection_time
                    else None
                ),
                "buffer_size": len(self.data_buffer),
                "buffer_capacity": self.buffer_size,
                "sources": {},
            }

            for source, metrics in self.integration_metrics.items():
                success_rate = (
                    metrics.successful_requests / metrics.total_requests
                    if metrics.total_requests > 0
                    else 0.0
                )

                summary["sources"][source.value] = {
                    "total_requests": metrics.total_requests,
                    "success_rate": success_rate,
                    "average_latency_ms": metrics.average_latency_ms,
                    "last_update": metrics.last_update.isoformat(),
                }

            return summary

        except Exception as e:
            logger.exception(f"Integration summary generation failed: {e}")
            return {"error": str(e)}
