"""
Unit tests for Performance Monitor.

Comprehensive test suite for performance monitoring, metrics collection,
alerting, and performance analysis functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from dgm_service.core.performance_monitor import PerformanceMonitor
from dgm_service.models.metrics import MetricAggregation, PerformanceMetric


@pytest.mark.unit
@pytest.mark.performance
class TestPerformanceMonitor:
    """Test suite for Performance Monitor."""

    @pytest.fixture
    def monitor(self):
        """Create performance monitor instance."""
        with patch.multiple(
            "dgm_service.core.performance_monitor",
            get_db=AsyncMock(),
            get_cache_manager=MagicMock(),
            PrometheusClient=MagicMock(),
        ):
            monitor = PerformanceMonitor()
            monitor.db_session = AsyncMock()
            monitor.cache_manager = AsyncMock()
            monitor.prometheus_client = MagicMock()
            return monitor

    @pytest.fixture
    def sample_metrics(self):
        """Sample performance metrics for testing."""
        return [
            {
                "metric_name": "response_time",
                "value": 125.5,
                "timestamp": datetime.utcnow(),
                "service_name": "dgm-service",
                "tags": {"endpoint": "/api/v1/dgm/improve"},
            },
            {
                "metric_name": "throughput",
                "value": 850.2,
                "timestamp": datetime.utcnow(),
                "service_name": "dgm-service",
                "tags": {"endpoint": "/api/v1/dgm/improve"},
            },
            {
                "metric_name": "error_rate",
                "value": 0.002,
                "timestamp": datetime.utcnow(),
                "service_name": "dgm-service",
                "tags": {"endpoint": "/api/v1/dgm/improve"},
            },
        ]

    async def test_record_metric_success(self, monitor):
        """Test successful metric recording."""
        metric_data = {
            "metric_name": "response_time",
            "value": 125.5,
            "service_name": "dgm-service",
            "tags": {"endpoint": "/api/v1/dgm/improve"},
        }

        # Mock database storage
        monitor.db_session.add.return_value = None
        monitor.db_session.commit.return_value = None

        # Mock cache storage
        monitor.cache_manager.set.return_value = True

        # Mock Prometheus recording
        monitor.prometheus_client.record_metric.return_value = None

        result = await monitor.record_metric(**metric_data)

        assert result is True

        # Verify database call
        monitor.db_session.add.assert_called_once()
        monitor.db_session.commit.assert_called_once()

        # Verify cache call
        monitor.cache_manager.set.assert_called_once()

        # Verify Prometheus call
        monitor.prometheus_client.record_metric.assert_called_once()

    async def test_record_metric_with_improvement_context(self, monitor):
        """Test metric recording with improvement context."""
        improvement_id = str(uuid4())

        metric_data = {
            "metric_name": "performance_gain",
            "value": 0.15,
            "improvement_id": improvement_id,
            "experiment_id": str(uuid4()),
            "service_name": "gs-service",
        }

        monitor.db_session.add.return_value = None
        monitor.db_session.commit.return_value = None

        result = await monitor.record_metric(**metric_data)

        assert result is True

        # Verify the metric was stored with improvement context
        call_args = monitor.db_session.add.call_args[0][0]
        assert call_args.improvement_id == improvement_id
        assert call_args.metric_name == "performance_gain"
        assert call_args.value == 0.15

    async def test_get_current_metrics(self, monitor):
        """Test retrieval of current performance metrics."""
        # Mock cache hit
        cached_metrics = {
            "response_time": 125.5,
            "throughput": 850.2,
            "error_rate": 0.002,
            "cpu_usage": 0.45,
            "memory_usage": 0.62,
            "timestamp": datetime.utcnow().isoformat(),
        }

        monitor.cache_manager.get.return_value = cached_metrics

        metrics = await monitor.get_current_metrics()

        assert metrics == cached_metrics
        monitor.cache_manager.get.assert_called_once_with("current_metrics")

    async def test_get_current_metrics_cache_miss(self, monitor):
        """Test current metrics retrieval with cache miss."""
        # Mock cache miss
        monitor.cache_manager.get.return_value = None

        # Mock database query
        mock_metrics = [
            MagicMock(metric_name="response_time", value=125.5, timestamp=datetime.utcnow()),
            MagicMock(metric_name="throughput", value=850.2, timestamp=datetime.utcnow()),
        ]

        monitor.db_session.execute.return_value.scalars.return_value.all.return_value = mock_metrics
        monitor.cache_manager.set.return_value = True

        metrics = await monitor.get_current_metrics()

        assert "response_time" in metrics
        assert "throughput" in metrics
        assert metrics["response_time"] == 125.5
        assert metrics["throughput"] == 850.2

        # Verify cache was updated
        monitor.cache_manager.set.assert_called_once()

    async def test_query_metrics_with_filters(self, monitor):
        """Test metric querying with various filters."""
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow()

        # Mock database query result
        mock_metrics = [
            MagicMock(
                metric_name="response_time",
                value=120.0,
                timestamp=start_time + timedelta(minutes=10),
                service_name="dgm-service",
            ),
            MagicMock(
                metric_name="response_time",
                value=130.0,
                timestamp=start_time + timedelta(minutes=20),
                service_name="dgm-service",
            ),
        ]

        monitor.db_session.execute.return_value.scalars.return_value.all.return_value = mock_metrics

        result = await monitor.query_metrics(
            metric_name="response_time",
            start_time=start_time,
            end_time=end_time,
            service_filter="dgm-service",
            aggregation="avg",
        )

        assert "data_points" in result
        assert "summary" in result
        assert len(result["data_points"]) == 2
        assert result["summary"]["average"] == 125.0  # (120 + 130) / 2

    async def test_generate_performance_report(self, monitor):
        """Test performance report generation."""
        days = 7
        service_name = "dgm-service"

        # Mock aggregated metrics
        mock_aggregations = [
            MagicMock(
                metric_name="response_time",
                time_window="1h",
                value=125.0,
                count=100,
                min_value=95.0,
                max_value=180.0,
                window_start=datetime.utcnow() - timedelta(hours=1),
            ),
            MagicMock(
                metric_name="throughput",
                time_window="1h",
                value=850.0,
                count=100,
                min_value=750.0,
                max_value=950.0,
                window_start=datetime.utcnow() - timedelta(hours=1),
            ),
        ]

        monitor.db_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_aggregations
        )

        report = await monitor.generate_report(days=days, service_name=service_name)

        assert "period_start" in report
        assert "period_end" in report
        assert "metrics" in report
        assert "summary" in report
        assert "trends" in report

        # Verify time period
        period_start = datetime.fromisoformat(report["period_start"])
        period_end = datetime.fromisoformat(report["period_end"])
        assert (period_end - period_start).days == days

    async def test_start_monitoring_background_task(self, monitor):
        """Test background monitoring task startup."""
        with patch.object(monitor, "_monitoring_loop") as mock_loop:
            mock_loop.return_value = None

            # Start monitoring
            await monitor.start_monitoring()

            # Verify monitoring loop was started
            mock_loop.assert_called_once()

    async def test_monitoring_loop_execution(self, monitor):
        """Test monitoring loop execution."""
        # Mock system metrics collection
        with patch.object(monitor, "_collect_system_metrics") as mock_collect:
            mock_collect.return_value = {
                "cpu_usage": 0.45,
                "memory_usage": 0.62,
                "disk_usage": 0.35,
            }

            with patch.object(monitor, "_check_alert_conditions") as mock_alerts:
                mock_alerts.return_value = []

                # Mock asyncio.sleep to prevent infinite loop
                with patch("asyncio.sleep", side_effect=[None, Exception("Stop loop")]):
                    try:
                        await monitor._monitoring_loop()
                    except Exception:
                        pass  # Expected to break the loop

        # Verify metrics collection was called
        mock_collect.assert_called()
        mock_alerts.assert_called()

    async def test_alert_condition_checking(self, monitor):
        """Test alert condition checking."""
        current_metrics = {
            "response_time": 250.0,  # High response time
            "error_rate": 0.05,  # High error rate
            "cpu_usage": 0.95,  # High CPU usage
            "memory_usage": 0.85,  # High memory usage
        }

        alerts = await monitor._check_alert_conditions(current_metrics)

        assert len(alerts) > 0

        # Check for specific alert types
        alert_types = [alert["type"] for alert in alerts]
        assert "high_response_time" in alert_types
        assert "high_error_rate" in alert_types
        assert "high_cpu_usage" in alert_types

    async def test_metric_aggregation(self, monitor):
        """Test metric aggregation functionality."""
        metric_name = "response_time"
        time_window = "1h"

        # Mock raw metrics
        raw_metrics = [
            {"value": 120.0, "timestamp": datetime.utcnow()},
            {"value": 130.0, "timestamp": datetime.utcnow()},
            {"value": 140.0, "timestamp": datetime.utcnow()},
            {"value": 110.0, "timestamp": datetime.utcnow()},
        ]

        aggregation = await monitor._aggregate_metrics(raw_metrics, metric_name, time_window)

        assert aggregation["metric_name"] == metric_name
        assert aggregation["time_window"] == time_window
        assert aggregation["count"] == 4
        assert aggregation["value"] == 125.0  # Average
        assert aggregation["min_value"] == 110.0
        assert aggregation["max_value"] == 140.0

    async def test_performance_baseline_establishment(self, monitor):
        """Test performance baseline establishment."""
        # Mock historical metrics
        historical_metrics = {
            "response_time": [120.0, 125.0, 130.0, 115.0, 135.0],
            "throughput": [800.0, 850.0, 820.0, 880.0, 790.0],
            "error_rate": [0.001, 0.002, 0.001, 0.003, 0.002],
        }

        with patch.object(monitor, "_get_historical_metrics") as mock_historical:
            mock_historical.return_value = historical_metrics

            baseline = await monitor.establish_baseline(days=30)

        assert "response_time" in baseline
        assert "throughput" in baseline
        assert "error_rate" in baseline

        # Verify baseline calculations
        assert baseline["response_time"]["mean"] == 125.0
        assert baseline["response_time"]["std"] > 0
        assert baseline["throughput"]["mean"] == 828.0

    async def test_performance_comparison(self, monitor):
        """Test performance comparison against baseline."""
        baseline = {
            "response_time": {"mean": 125.0, "std": 10.0},
            "throughput": {"mean": 850.0, "std": 50.0},
            "error_rate": {"mean": 0.002, "std": 0.001},
        }

        current_metrics = {
            "response_time": 110.0,  # Better than baseline
            "throughput": 900.0,  # Better than baseline
            "error_rate": 0.001,  # Better than baseline
        }

        comparison = await monitor.compare_to_baseline(current_metrics, baseline)

        assert comparison["overall_improvement"] > 0
        assert comparison["response_time_improvement"] > 0
        assert comparison["throughput_improvement"] > 0
        assert comparison["error_rate_improvement"] > 0

    async def test_metric_retention_policy(self, monitor):
        """Test metric retention policy enforcement."""
        retention_days = 30
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Mock database cleanup
        monitor.db_session.execute.return_value.rowcount = 1500
        monitor.db_session.commit.return_value = None

        deleted_count = await monitor.cleanup_old_metrics(retention_days)

        assert deleted_count == 1500
        monitor.db_session.execute.assert_called()
        monitor.db_session.commit.assert_called()

    async def test_constitutional_compliance_metrics(self, monitor):
        """Test constitutional compliance metrics recording."""
        compliance_data = {
            "improvement_id": str(uuid4()),
            "compliance_score": 0.95,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "validation_time": 2.5,
        }

        await monitor.record_compliance_metrics(**compliance_data)

        # Verify compliance metrics were recorded
        monitor.db_session.add.assert_called()

        # Check the recorded metric
        call_args = monitor.db_session.add.call_args[0][0]
        assert call_args.improvement_id == compliance_data["improvement_id"]
        assert call_args.constitutional_compliance_score == 0.95

    async def test_error_handling_in_monitoring(self, monitor):
        """Test error handling in monitoring operations."""
        # Mock database error
        monitor.db_session.add.side_effect = Exception("Database error")

        # Should not raise exception, but log error
        with patch("logging.getLogger") as mock_logger:
            logger_instance = mock_logger.return_value

            result = await monitor.record_metric(metric_name="test_metric", value=100.0)

            assert result is False
            logger_instance.error.assert_called()

    @pytest.mark.slow
    async def test_high_volume_metric_recording(self, monitor):
        """Test performance with high volume metric recording."""
        import asyncio

        # Mock successful database operations
        monitor.db_session.add.return_value = None
        monitor.db_session.commit.return_value = None
        monitor.cache_manager.set.return_value = True

        # Create many concurrent metric recording tasks
        tasks = []
        for i in range(100):
            task = monitor.record_metric(
                metric_name=f"test_metric_{i % 10}", value=float(i), service_name="test-service"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all metrics were recorded successfully
        successful_recordings = sum(1 for result in results if result is True)
        assert successful_recordings == 100

    async def test_metrics_summary_generation(self, monitor):
        """Test metrics summary generation."""
        start_time = datetime.utcnow() - timedelta(hours=24)
        end_time = datetime.utcnow()
        service_name = "dgm-service"

        # Mock aggregated data
        with patch.object(monitor, "_get_aggregated_metrics") as mock_agg:
            mock_agg.return_value = {
                "response_time": {"avg": 125.0, "min": 95.0, "max": 180.0},
                "throughput": {"avg": 850.0, "min": 750.0, "max": 950.0},
                "error_rate": {"avg": 0.002, "min": 0.0, "max": 0.01},
            }

            summary = await monitor.get_metrics_summary(
                start_time=start_time, end_time=end_time, service_name=service_name
            )

        assert "metrics" in summary
        assert "trends" in summary
        assert "alerts" in summary
        assert "constitutional_compliance_score" in summary

        # Verify metric summaries
        assert summary["metrics"]["response_time"]["avg"] == 125.0
        assert summary["metrics"]["throughput"]["avg"] == 850.0
